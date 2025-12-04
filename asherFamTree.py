import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime
import json
import re
import os

# Version 1.2 - Fully fixed indentation and features
# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Interactive Family Tree Editor", page_icon="🌳")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🌳 Asher Family Digital Lineage System</h1>', unsafe_allow_html=True)

# Display original document on main page
original_img_path = "original_tree.jpg"
if os.path.exists(original_img_path):
    with st.expander("📜 View Original Handwritten Document", expanded=False):
        st.image(original_img_path, caption="Original Asher Family Tree Document", use_container_width=True)

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["📝 Data Entry", "🕸️ Family Tree", "📊 Statistics", "ℹ️ Help"])

# --- 1. Load and Transform Family Data from JSON ---
def parse_lifespan(lifespan_str):
    """Parse lifespan string like '1850-1914' or '1975-' into birth and death years"""
    if not lifespan_str or lifespan_str == "?":
        return None, None

    lifespan_str = str(lifespan_str).strip()
    match = re.match(r'(\d{4})\s*[-–]\s*(\d{4}|\?)?', lifespan_str)
    if match:
        birth = int(match.group(1)) if match.group(1) else None
        death = int(match.group(2)) if match.group(2) and match.group(2) != '?' else None
        return birth, death

    match = re.match(r'(\d{4})', lifespan_str)
    if match:
        return int(match.group(1)), None

    return None, None


def infer_gender(name, spouse_info=None):
    """Infer gender from name patterns or spouse description"""
    male_patterns = [
        'Yosef', 'Moshe', 'Haim', 'David', 'Itzchak', 'Jack', 'Jacques',
        'Allen', 'Herbert', 'Alberto', 'Nathan', 'Samuel', 'Benjamin',
        'Jacob', 'Abraham', 'Isaac', 'Aaron', 'Daniel', 'Michael', 'Robert',
        'Ephraim', 'Elia', 'Eli', 'Alan', 'Leonard', 'Eddie', 'Alon', 'Eitan'
    ]

    female_patterns = [
        'Rivka', 'Ester', 'Matilda', 'Sara', 'Rachel', 'Bella', 'Gloria',
        'Wendy', 'Rebecca', 'Miriam', 'Hannah', 'Sarah', 'Ruth', 'Naomi',
        'Esther', 'Leah', 'Deborah', 'Susan', 'Linda', 'Nancy', 'Elizabeth',
        'Becki', 'Joyce', 'Marlene', 'Eram'
    ]

    name_lower = name.lower() if name else ""
    if any(pattern.lower() in name_lower for pattern in male_patterns):
        return "Male"
    if any(pattern.lower() in name_lower for pattern in female_patterns):
        return "Female"

    spouse_text = str(spouse_info).lower() if spouse_info else ""
    if "wife" in spouse_text:
        return "Male"
    if "husband" in spouse_text:
        return "Female"

    return "Unknown"


def load_family_data_from_json():
    """Load and transform family data from JSON file"""
    json_path = "family_data.json"
    if not os.path.exists(json_path):
        st.warning(f"JSON file not found at: {os.path.abspath(json_path)}")
        return create_sample_data()

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = re.sub(r'//.*?\n', '\n', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            json_data = json.loads(content)

        id_to_name = {person['id']: person['name'] for person in json_data}
        transformed = []
        for person in json_data:
            birth, death = parse_lifespan(person.get('lifespan', ''))
            parent_name = id_to_name.get(person.get('parent_id')) if person.get('parent_id') else None
            spouse = person.get('spouse')
            gender = infer_gender(person.get('name', ''), spouse)
            transformed.append({
                "Name": person.get('name'),
                "Parent": parent_name,
                "Birth": birth,
                "Death": death,
                "Location": person.get('location', 'Unknown'),
                "Gender": gender,
                "Spouse": spouse,
                "Occupation": person.get('occupation'),
                "Photo": person.get('photo'),
                "Generation": person.get('generation', 1),
                "Highlight": person.get('highlighted', False),
                "Notes": person.get('note', '')
            })

        return transformed

    except Exception as e:
        st.error(f"Error loading JSON file: {str(e)}")
        return create_sample_data()


def create_sample_data():
    """Create sample data if JSON file is not available"""
    return [
        {
            "Name": "Yosef Acher",
            "Parent": None,
            "Birth": 1775,
            "Death": None,
            "Location": "Unknown",
            "Gender": "Male",
            "Spouse": None,
            "Occupation": None,
            "Photo": None,
            "Generation": 1,
            "Highlight": False,
            "Notes": "Patriarch of the Acher family"
        }
    ]


def validate_dates(df):
    """Validate date consistency in family tree"""
    errors = []
    for _, row in df.iterrows():
        if pd.notna(row.get('Birth')) and pd.notna(row.get('Death')):
            if row['Death'] < row['Birth']:
                errors.append(f"❌ {row['Name']}: Death year ({row['Death']}) precedes birth year ({row['Birth']})")

        if pd.notna(row.get('Parent')) and pd.notna(row.get('Birth')):
            parent_rows = df[df['Name'] == row['Parent']]
            if not parent_rows.empty:
                parent_birth = parent_rows.iloc[0].get('Birth')
                if pd.notna(parent_birth) and row['Birth'] < parent_birth + 15:
                    errors.append(f"⚠️ {row['Name']}: Born when parent was under 15 years old")
    return errors


def calculate_generation(df):
    """Automatically calculate generation levels"""
    generation_map = {}
    roots = df[df['Parent'].isna() | (df['Parent'] == '')]['Name'].tolist()
    for root in roots:
        generation_map[root] = 1

    changed = True
    while changed:
        changed = False
        for _, row in df.iterrows():
            parent = row.get('Parent')
            name = row.get('Name')
            if name not in generation_map and parent in generation_map:
                generation_map[name] = generation_map[parent] + 1
                changed = True
    return generation_map


# Load initial data and seed session state
initial_data = load_family_data_from_json()
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(initial_data)
if 'first_run' not in st.session_state:
    st.session_state.first_run = True
if 'update_viz' not in st.session_state:
    st.session_state.update_viz = True

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reload Original Data"):
    st.session_state.df = pd.DataFrame(load_family_data_from_json())
    st.rerun()

with tab1:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📝 Family Member Data")

        # Configure column types for the data editor
        column_config = {
            "Name": st.column_config.TextColumn("Full Name", required=True, help="Person's full name"),
            "Parent": st.column_config.TextColumn("Parent Name", help="Leave empty for root ancestors"),
            "Birth": st.column_config.NumberColumn("Birth Year", min_value=1000, max_value=2024, format="%d"),
            "Death": st.column_config.NumberColumn("Death Year", min_value=1000, max_value=2024, format="%d"),
            "Gender": st.column_config.SelectboxColumn("Gender", options=["Male", "Female", "Unknown"]),
            "Location": st.column_config.TextColumn("Location", help="Birth or residence location"),
            "Spouse": st.column_config.TextColumn("Spouse Name", help="Name of spouse"),
            "Occupation": st.column_config.TextColumn("Occupation", help="Primary occupation"),
            "Photo": st.column_config.LinkColumn("Photo URL", help="Link to photo (must be https://...)"),
            "Generation": st.column_config.NumberColumn("Generation", min_value=1, max_value=20),
            "Highlight": st.column_config.CheckboxColumn("Highlight", help="Highlight in visualization"),
            "Notes": st.column_config.TextColumn("Notes", help="Additional information")
        }

        # Add "Quick Add" expandable form
        with st.expander("➕ Quick Add Family Member"):
            with st.form("add_member_form"):
                c1, c2, c3 = st.columns(3)
                new_name = c1.text_input("Full Name")
                new_parent = c2.selectbox("Parent", [""] + sorted(st.session_state.df['Name'].astype(str).unique().tolist()))
                new_gender = c3.selectbox("Gender", ["Male", "Female", "Unknown"])

                c4, c5, c6 = st.columns(3)
                new_birth = c4.number_input("Birth Year", min_value=1700, max_value=2025, value=None, placeholder="YYYY")
                new_death = c5.number_input("Death Year", min_value=1700, max_value=2025, value=None, placeholder="Living")
                new_location = c6.text_input("Location")

                new_photo = st.text_input("Photo URL (optional)")

                if st.form_submit_button("Add Member"):
                    if new_name:
                        new_row = {
                            "Name": new_name,
                            "Parent": new_parent if new_parent else None,
                            "Birth": new_birth,
                            "Death": new_death,
                            "Location": new_location,
                            "Gender": new_gender,
                            "Photo": new_photo,
                            "Generation": 1,  # Placeholder, will be auto-calculated
                            "Highlight": False
                        }
                        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                        st.success(f"Added {new_name}!")
                        st.rerun()
                    else:
                        st.error("Name is required!")

        edited_df = st.data_editor(
            st.session_state.df,
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="data_editor"
        )

        # Auto-calculate generations button
        if st.button("🔢 Auto-Calculate Generations"):
            gen_map = calculate_generation(edited_df)
            for idx, row in edited_df.iterrows():
                if row['Name'] in gen_map:
                    edited_df.at[idx, 'Generation'] = gen_map[row['Name']]
            st.session_state.df = edited_df
            st.rerun()
        
    with col2:
        st.subheader("🔍 Data Validation")

        # Validate the data
        validation_errors = validate_dates(edited_df)

        if validation_errors:
            st.error("Data Issues Found:")
            for error in validation_errors:
                st.write(error)
        else:
            st.success("✅ All data validated successfully!")

        # Quick stats
        st.metric("Total Members", len(edited_df))
        st.metric("Generations", edited_df['Generation'].max() if not edited_df.empty else 0)
        st.metric("Living Members", len(edited_df[edited_df['Death'].isna()]))
# --- 3. Sidebar Customization ---
st.sidebar.header("🎨 Visualization Settings")
st.sidebar.subheader("Color Scheme")

# Generation-based coloring option
color_by = st.sidebar.radio("Color nodes by:", ["Generation", "Highlight", "Gender", "Location"])

if color_by == "Highlight":
    highlight_color = st.sidebar.color_picker("Highlight Color", "#E8B04B")  # Warm gold
    default_color = st.sidebar.color_picker("Default Node Color", "#8FA4B1")  # Muted blue-gray

# Professional background colors
bg_color = st.sidebar.color_picker("Background Color", "#FAFAFA")  # Off-white for better readability
edge_color = st.sidebar.color_picker("Edge Color", "#8C8C8C")  # Medium gray for edges

st.sidebar.subheader("Layout Options")
layout_type = st.sidebar.selectbox("Layout Style", 
    ["Hierarchical (Tree)", "Physics (Organic)", "Circular", "Random"])

if layout_type == "Hierarchical (Tree)":
    tree_direction = st.sidebar.selectbox("Tree Direction", ["Top-Down", "Left-Right", "Bottom-Up", "Right-Left"])
    node_spacing = st.sidebar.slider("Node Spacing", 50, 300, 150)

st.sidebar.subheader("Display Options")
show_lifespan = st.sidebar.checkbox("Show Lifespan in Labels", value=True)
show_generation = st.sidebar.checkbox("Show Generation Number", value=True)
node_size_by_descendants = st.sidebar.checkbox("Size nodes by number of descendants", value=False)
text_size = st.sidebar.slider("Text Size", 10, 28, 16, step=2)

# --- 4. Enhanced Graph Generation Logic ---
def count_descendants(df, person_name):
    """Count all descendants of a person"""
    descendants = set()
    to_check = [person_name]
    
    while to_check:
        current = to_check.pop()
        children = df[df['Parent'] == current]['Name'].tolist()
        for child in children:
            if child not in descendants:
                descendants.add(child)
                to_check.append(child)
    
    return len(descendants)

def get_node_color(row, color_by, highlight_color="#E8B04B", default_color="#8FA4B1"):
    """Determine node color based on selected criteria"""
    # Professional genealogical color palettes
    
    # Warm earth tones for generations (commonly used in genealogy)
    generation_colors = {
        1: "#8B4513",  # Saddle Brown - oldest generation
        2: "#A0522D",  # Sienna
        3: "#BC8F8F",  # Rosy Brown
        4: "#CD853F",  # Peru
        5: "#DEB887",  # Burlewood
        6: "#F4A460",  # Sandy Brown
        7: "#FFE4B5",  # Moccasin - youngest generation
        8: "#FFDEAD",  # Navajo White
        9: "#FFE4C4"   # Bisque
    }
    
    # Subtle, professional gender colors
    gender_colors = {
        "Male": "#6B8CAE",    # Muted steel blue
        "Female": "#D4A5A5",  # Dusty rose
        "Unknown": "#C0C0C0"  # Silver gray
    }
    
    # Geographical colors with better harmony
    location_colors = {
        "Israel": "#5B8FA8",     # Teal blue
        "USA": "#9B7653",        # Tan brown
        "Brazil": "#8FA068",     # Sage green
        "Unknown": "#A8A8A8",    # Medium gray
        "Europe": "#7D6B91",     # Muted purple
        "Asia": "#C17E61",       # Terra cotta
        "Africa": "#7A9A65"      # Olive green
    }
    
    if color_by == "Generation":
        gen = row.get('Generation', 1)
        return generation_colors.get(gen, "#DEB887")  # Default to a middle generation color
    elif color_by == "Gender":
        return gender_colors.get(row.get('Gender', 'Unknown'), "#C0C0C0")
    elif color_by == "Location":
        loc = row.get('Location', 'Unknown')
        # Try to match location keywords
        for key in location_colors:
            if key.lower() in str(loc).lower():
                return location_colors[key]
        return location_colors.get('Unknown')
    else:  # Highlight
        return highlight_color if row.get('Highlight', False) else default_color

def generate_graph_html(dataframe):
    """Generate the interactive family tree visualization using D3.js"""
    # Determine font color based on background brightness
    bg_brightness = int(bg_color[1:3], 16) + int(bg_color[3:5], 16) + int(bg_color[5:7], 16)
    font_color = "#2C3E50" if bg_brightness > 384 else "#ECEFF1"

    # Calculate descendants for sizing if needed
    descendants_count = {}
    if node_size_by_descendants:
        for _, row in dataframe.iterrows():
            descendants_count[row['Name']] = count_descendants(dataframe, row['Name'])

    # Build nodes array
    nodes = []
    node_ids = {}
    for idx, row in dataframe.iterrows():
        node_name = str(row['Name']).strip() if pd.notna(row['Name']) else ""
        if not node_name:
            continue

        node_ids[node_name] = len(nodes)

        # Create detailed tooltip
        birth = f"{int(row['Birth'])}" if pd.notna(row['Birth']) else "?"
        death = f"{int(row['Death'])}" if pd.notna(row['Death']) else "Living"
        age = f" (Age: {int(row['Death']) - int(row['Birth'])})" if pd.notna(row['Birth']) and pd.notna(row['Death']) else ""

        tooltip_parts = [node_name]
        if pd.notna(row.get('Gender')):
            tooltip_parts.append(f"Gender: {row['Gender']}")
        tooltip_parts.append(f"Born: {birth}")
        tooltip_parts.append(f"Died: {death}{age}")
        if pd.notna(row.get('Location')):
            tooltip_parts.append(f"Location: {row['Location']}")
        if pd.notna(row.get('Spouse')):
            tooltip_parts.append(f"Spouse: {row['Spouse']}")
        if show_generation and pd.notna(row.get('Generation')):
            tooltip_parts.append(f"Generation: {int(row['Generation'])}")

        tooltip = "\\n".join(tooltip_parts)

        # Create label
        label_parts = [node_name]
        if show_lifespan:
            label_parts.append(f"({birth}-{death})")
        if show_generation and pd.notna(row.get('Generation')):
            label_parts.append(f"Gen {int(row['Generation'])}")

        # Determine node size
        if node_size_by_descendants:
            size = 8 + min(descendants_count.get(node_name, 0) * 2, 30)
        else:
            size = 12

        # Get node color
        if color_by == "Highlight" and 'highlight_color' in globals() and 'default_color' in globals():
            color = get_node_color(row, color_by, highlight_color, default_color)
        else:
            color = get_node_color(row, color_by)

        # Get generation for Y positioning
        gen = int(row.get('Generation', 1)) if pd.notna(row.get('Generation')) else 1

        node = {
            "id": node_name,
            "name": node_name,
            "label": label_parts,
            "tooltip": tooltip,
            "color": color,
            "size": size,
            "gender": row.get('Gender', 'Unknown'),
            "generation": gen
        }
        nodes.append(node)

    # Build links array
    links = []
    for _, row in dataframe.iterrows():
        node_name = str(row['Name']).strip() if pd.notna(row['Name']) else ""
        parent_name = str(row['Parent']).strip() if pd.notna(row['Parent']) else ""

        if node_name and parent_name and parent_name.lower() not in ["none", ""] and node_name in node_ids and parent_name in node_ids:
            links.append({
                "source": parent_name,
                "target": node_name,
                "type": "parent"
            })

    # Generate the complete HTML with D3.js
    nodes_json = json.dumps(nodes)
    links_json = json.dumps(links)

    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 100%; height: 100%; overflow: hidden; }}
        svg {{ width: 100%; height: 100%; background-color: {bg_color}; display: block; }}
        .node {{ cursor: pointer; }}
        .node ellipse {{ stroke: #333; stroke-width: 2px; }}
        .node rect {{ stroke: #333; stroke-width: 2px; }}
        .node text {{ font-family: Arial, sans-serif; font-size: {text_size}px; fill: #000000; font-weight: bold; pointer-events: none; text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff; }}
        .link {{ fill: none; stroke: {edge_color}; stroke-width: 2px; }}
        .tooltip {{ position: absolute; background: rgba(0,0,0,0.9); color: white; padding: 10px 14px; border-radius: 6px; font-size: 14px; pointer-events: none; white-space: pre-line; max-width: 300px; z-index: 1000; }}
    </style>
</head>
<body>
    <svg id="tree"></svg>
    <script>
        const nodes = {nodes_json};
        const links = {links_json};

        // Calculate dynamic width based on largest generation
        const generations = {{}};
        nodes.forEach(n => {{
            if (!generations[n.generation]) generations[n.generation] = [];
            generations[n.generation].push(n);
        }});

        // Find max nodes in any generation for width calculation
        const maxNodesInGen = Math.max(...Object.values(generations).map(g => g.length));
        const nodeWidth = 180; // Minimum width per node
        const dynamicWidth = Math.max(1200, maxNodesInGen * nodeWidth);
        const height = 800;

        const svg = d3.select("#tree")
            .attr("viewBox", [0, 0, dynamicWidth, height]);

        // Create container for zoom
        const g = svg.append("g");

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => g.attr("transform", event.transform));
        svg.call(zoom);

        // Create tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        const levelHeight = 140;
        const startY = 80;

        // Position nodes with dynamic spacing based on generation size
        Object.keys(generations).sort((a,b) => a-b).forEach(gen => {{
            const genNodes = generations[gen];
            const spacing = dynamicWidth / (genNodes.length + 1);
            genNodes.forEach((n, i) => {{
                n.x = spacing * (i + 1);
                n.y = startY + (gen - 1) * levelHeight;
            }});
        }});

        // Create node map for links
        const nodeMap = {{}};
        nodes.forEach(n => nodeMap[n.id] = n);

        // Draw links
        const link = g.append("g")
            .selectAll("path")
            .data(links)
            .join("path")
            .attr("class", "link")
            .attr("d", d => {{
                const source = nodeMap[d.source];
                const target = nodeMap[d.target];
                if (!source || !target) return "";
                const midY = (source.y + target.y) / 2;
                return `M${{source.x}},${{source.y + 30}} C${{source.x}},${{midY}} ${{target.x}},${{midY}} ${{target.x}},${{target.y - 30}}`;
            }});

        // Draw nodes
        const node = g.append("g")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${{d.x}},${{d.y}})`)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Add shapes based on gender - larger sizes
        node.each(function(d) {{
            const el = d3.select(this);
            const baseSize = d.size + 10;
            if (d.gender === "Female") {{
                el.append("ellipse")
                    .attr("rx", baseSize + 20)
                    .attr("ry", baseSize + 5)
                    .attr("fill", d.color);
            }} else {{
                el.append("rect")
                    .attr("x", -(baseSize + 15))
                    .attr("y", -(baseSize))
                    .attr("width", (baseSize + 15) * 2)
                    .attr("height", (baseSize) * 2)
                    .attr("rx", 5)
                    .attr("fill", d.color);
            }}
        }});

        // Add labels - text size controlled by slider
        const textSize = {text_size};
        const lineHeight = textSize + 4;
        node.each(function(d) {{
            const el = d3.select(this);
            d.label.forEach((line, i) => {{
                el.append("text")
                    .attr("dy", (i - d.label.length/2 + 0.5) * lineHeight)
                    .attr("text-anchor", "middle")
                    .text(line);
            }});
        }});

        // Tooltip events
        node.on("mouseover", (event, d) => {{
            tooltip.transition().duration(200).style("opacity", 1);
            tooltip.html(d.tooltip)
                .style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 15) + "px");
        }})
        .on("mouseout", () => {{
            tooltip.transition().duration(500).style("opacity", 0);
        }});

        // Drag functions
        function dragstarted(event, d) {{
            d3.select(this).raise();
        }}

        function dragged(event, d) {{
            d.x = event.x;
            d.y = event.y;
            d3.select(this).attr("transform", `translate(${{d.x}},${{d.y}})`);
            link.attr("d", l => {{
                const source = nodeMap[l.source];
                const target = nodeMap[l.target];
                if (!source || !target) return "";
                const midY = (source.y + target.y) / 2;
                return `M${{source.x}},${{source.y + 30}} C${{source.x}},${{midY}} ${{target.x}},${{midY}} ${{target.x}},${{target.y - 30}}`;
            }});
        }}

        function dragended(event, d) {{}}

        // Initial zoom to fit content
        const initialScale = Math.min(1, 900 / dynamicWidth);
        svg.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(initialScale));
    </script>
</body>
</html>'''
    return html

# --- 5. Render the Graph in Tab 2 ---
with tab2:
    # Center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Generate/Update Family Tree Visualization", type="primary", use_container_width=True):
            st.session_state.update_viz = True

    # Display graph at full width (outside column constraint)
    if st.session_state.get('update_viz', False) or st.session_state.get('first_run', True):
        st.session_state.first_run = False

        if edited_df.empty:
            st.warning("⚠️ No data available. Please add family members in the Data Entry tab.")
        else:
            with st.spinner("🔄 Generating family tree visualization..."):
                try:
                    graph_html = generate_graph_html(edited_df)

                    # Add search functionality
                    st.subheader("🔍 Search Family Members")
                    search_col1, search_col2 = st.columns(2)
                    with search_col1:
                        search_term = st.text_input("Search by name:", placeholder="Enter name...")
                    with search_col2:
                        search_gen = st.selectbox(
                            "Filter by generation:",
                            ["All"] + list(range(1, int(edited_df['Generation'].max()) + 1))
                            if not edited_df.empty else ["All"]
                        )

                    # Display the interactive graph
                    st.subheader("🌳 Interactive Family Tree Visualization")
                    st.info("💡 **Tip:** Drag nodes to rearrange, scroll to zoom, click and drag background to pan")

                    # Render the HTML content
                    components.html(graph_html, height=750, scrolling=False)
                    st.session_state.update_viz = False

                except Exception as e:
                    st.error(f"Error generating visualization: {str(e)}")
# --- 6. Statistics Tab ---
with tab3:
    st.subheader("📊 Family Tree Statistics & Analysis")
    
    if not edited_df.empty:
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Members", len(edited_df))
            st.metric("🎯 Living Members", len(edited_df[edited_df['Death'].isna()]))
        
        with col2:
            st.metric("🔢 Generations", int(edited_df['Generation'].max()) if 'Generation' in edited_df else "N/A")
            avg_lifespan = edited_df[edited_df['Death'].notna()].apply(
                lambda x: x['Death'] - x['Birth'] if pd.notna(x['Birth']) else None, axis=1
            ).mean()
            st.metric("📅 Avg Lifespan", f"{avg_lifespan:.0f} years" if pd.notna(avg_lifespan) else "N/A")
        
        with col3:
            male_count = len(edited_df[edited_df['Gender'] == 'Male'])
            female_count = len(edited_df[edited_df['Gender'] == 'Female'])
            st.metric("👨 Males", male_count)
            st.metric("👩 Females", female_count)
        
        with col4:
            locations = edited_df['Location'].value_counts().head(3)
            st.metric("📍 Top Location", locations.index[0] if len(locations) > 0 else "N/A")
            st.metric("🌍 Unique Locations", edited_df['Location'].nunique())
        
        st.markdown("---")
        
        # Generation breakdown
        st.subheader("Generation Analysis")
        gen_df = edited_df.groupby('Generation').agg({
            'Name': 'count',
            'Birth': lambda x: f"{x.min():.0f}-{x.max():.0f}" if x.notna().any() else "N/A"
        }).rename(columns={'Name': 'Count', 'Birth': 'Birth Year Range'})
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(gen_df, use_container_width=True)
        
        with col2:
            # Create a simple bar chart using Streamlit
            if 'Generation' in edited_df.columns:
                gen_counts = edited_df['Generation'].value_counts().sort_index()
                st.bar_chart(gen_counts)
        
        # Family branches analysis
        st.subheader("Family Branches")
        
        # Find family branches (children of Generation 1-2)
        early_gen = edited_df[edited_df['Generation'] <= 2]['Name'].tolist()
        branch_data = []
        
        for ancestor in early_gen:
            descendants = count_descendants(edited_df, ancestor)
            if descendants > 0:
                branch_data.append({
                    'Ancestor': ancestor,
                    'Descendants': descendants,
                    'Birth Year': edited_df[edited_df['Name'] == ancestor]['Birth'].values[0] if len(edited_df[edited_df['Name'] == ancestor]) > 0 else None
                })
        
        if branch_data:
            branch_df = pd.DataFrame(branch_data)
            st.dataframe(branch_df, use_container_width=True)
    else:
        st.info("📝 Please add family data in the Data Entry tab to see statistics.")

# --- 7. Help Tab ---
with tab4:
    st.subheader("ℹ️ How to Use This Family Tree System")
    
    st.markdown("""
    ### Getting Started
    
    1. **Data Entry Tab** 📝
       - Add new family members by clicking the "+" button in the data table
       - Fill in all available information for accuracy
       - Use the "Auto-Calculate Generations" button to automatically number generations
       - Parent names must match exactly (case-sensitive)
    
    2. **Family Tree Tab** 🌳
       - Click "Generate/Update Family Tree Visualization" to create the tree
       - Drag nodes to rearrange the layout
       - Scroll to zoom in/out
       - Click on nodes to see detailed information
       - Different shapes represent genders (square=male, circle=female, box=unknown)
    
    3. **Statistics Tab** 📊
       - View comprehensive family statistics
       - Analyze generation patterns
       - See family branch breakdowns
    
    ### Data Fields Explained
    
    - **Name**: Full name of the person
    - **Parent**: Name of one parent (must match exactly)
    - **Birth/Death**: Year of birth and death (leave Death empty for living persons)
    - **Gender**: Male, Female, or Unknown
    - **Location**: Birth location or primary residence
    - **Spouse**: Name of spouse (optional)
    - **Occupation**: Primary occupation (optional)
    - **Generation**: Generational level (1 = oldest ancestors)
    - **Highlight**: Check to highlight in yellow
    - **Notes**: Any additional information
    
    ### Tips for Genealogists
    
    - 🔍 **Research Tips**: Start with what you know and work backwards
    - 📅 **Date Validation**: The system checks for logical date consistency
    - 🌍 **Location Tracking**: Include countries/cities for migration patterns
    - 👥 **Relationship Mapping**: Currently supports parent-child and spouse relationships
    - 📝 **Documentation**: Use the Notes field for sources and references
    
    ### Color Coding Options
    
    - **By Generation**: Each generation gets a different color
    - **By Gender**: Blue for males, pink for females, gray for unknown
    - **By Location**: Different colors for different locations
    - **By Highlight**: Manual highlighting for important individuals
    
    ### Export and Import
    
    - Use the sidebar download button to save your work as CSV
    - Import CSV files by copying data into the table
    - Regular backups are recommended
    """)

# --- 8. Export Data Option in Sidebar ---
st.sidebar.markdown("---")
st.sidebar.header("💾 Data Management")

# Save as CSV
csv = edited_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    "📥 Download as CSV",
    csv,
    "asher_family_tree.csv",
    "text/csv",
    key='download-csv'
)

# Save as JSON (more structured)
json_data = edited_df.to_json(orient='records', indent=2)
st.sidebar.download_button(
    "📥 Download as JSON",
    json_data,
    "asher_family_tree.json",
    "application/json",
    key='download-json'
)

# Upload data option
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📤 Upload Family Data", type=['csv', 'json'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            new_df = pd.read_csv(uploaded_file)
        else:
            new_df = pd.read_json(uploaded_file)
        
        st.session_state.df = new_df
        st.sidebar.success("✅ Data loaded successfully!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error loading file: {str(e)}")
