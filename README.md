# Asher Family Digital Lineage System 🌳

An interactive family tree visualization and genealogy management system built with Python and Streamlit.

## Features

### 📊 Comprehensive Genealogical Data Management
- **Enhanced data fields**: Name, birth/death years, gender, location, spouse, occupation, generation, and notes
- **Automatic generation calculation**: Intelligently determines generation levels
- **Data validation**: Ensures chronological consistency (birth before death, parent-child age gaps)
- **Dynamic data editing**: Add, modify, or remove family members in real-time

### 🌳 Advanced Visualization Options
- **Multiple layout styles**: Hierarchical tree, organic physics-based, circular, and random layouts
- **Color coding schemes**:
  - By generation (different color for each generation level)
  - By gender (blue for male, pink for female)
  - By location (geographic color coding)
  - Manual highlighting of important individuals
- **Interactive features**:
  - Drag nodes to rearrange
  - Zoom in/out with scroll
  - Pan by dragging the background
  - Click nodes for detailed information
- **Visual enhancements**:
  - Gender-specific node shapes (square for males, circle for females)
  - Lifespan display in labels
  - Spouse relationships shown with dashed lines
  - Node sizing by number of descendants

### 📈 Statistical Analysis
- **Family metrics**: Total members, living members, generation count, average lifespan
- **Demographic breakdown**: Gender distribution, location analysis
- **Generation analysis**: Member count and birth year ranges by generation
- **Family branch analysis**: Descendant counts for each ancestor

### 💾 Data Management
- **Export options**: Save as CSV or JSON format
- **Import capability**: Upload existing family data
- **Data persistence**: Maintains edits during session

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   cd /Users/eitan/Library/CloudStorage/GoogleDrive-eitanas85@gmail.com/My Drive/Personal/AsherFamily
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run asherFamTree.py
   ```

4. **Access the application**
   - The app will automatically open in your default browser
   - If not, navigate to `http://localhost:8501`

## Usage Guide

### Data Entry Tab
1. Add new family members using the "+" button
2. Fill in all available information:
   - **Name**: Full name (required)
   - **Parent**: Parent's name (must match exactly)
   - **Birth/Death**: Years (Death empty for living persons)
   - **Gender**: Male/Female/Unknown
   - **Location**: Birth or residence location
   - **Spouse**: Spouse's name (optional)
   - **Occupation**: Primary occupation (optional)
   - **Generation**: Auto-calculated or manual
   - **Highlight**: Check to emphasize in visualization
   - **Notes**: Additional information

3. Use "Auto-Calculate Generations" to number generations automatically
4. Monitor data validation panel for any issues

### Family Tree Tab
1. Click "Generate/Update Family Tree Visualization"
2. Customize visualization using sidebar options:
   - Choose color scheme (generation, gender, location, or manual)
   - Select layout style (tree, organic, circular, random)
   - Adjust tree direction and spacing
   - Toggle display options (lifespan, generation numbers, node sizing)

3. Interact with the tree:
   - Drag nodes to reposition
   - Scroll to zoom
   - Click and drag background to pan
   - Hover over nodes for detailed information

### Statistics Tab
- View comprehensive family statistics
- Analyze generation distributions
- Examine family branches and descendant counts

### Help Tab
- Access detailed instructions
- Learn about data fields and best practices
- Understand color coding options

## Data Format

### CSV Structure
The CSV file should contain the following columns:
- Name, Parent, Birth, Death, Location, Gender, Spouse, Occupation, Generation, Highlight, Notes

### JSON Structure
```json
[
  {
    "Name": "Person Name",
    "Parent": "Parent Name",
    "Birth": 1900,
    "Death": 1980,
    "Location": "City, Country",
    "Gender": "Male/Female/Unknown",
    "Spouse": "Spouse Name",
    "Occupation": "Occupation",
    "Generation": 1,
    "Highlight": false,
    "Notes": "Additional information"
  }
]
```

## Tips for Genealogists

1. **Start with known information**: Begin with yourself and work backwards
2. **Maintain consistency**: Ensure names are spelled consistently throughout
3. **Document sources**: Use the Notes field for references and sources
4. **Regular backups**: Export your data regularly to prevent loss
5. **Verify relationships**: Use the validation panel to check for logical inconsistencies
6. **Track migrations**: Use location field to document family movements
7. **Note uncertainties**: Use "?" or approximate dates when exact information is unknown

## Troubleshooting

### Common Issues

1. **Import errors for packages**
   - Ensure all packages from requirements.txt are installed
   - Try: `pip install --upgrade streamlit pandas pyvis networkx`

2. **Visualization not updating**
   - Click the "Generate/Update" button after making changes
   - Refresh the browser page if needed

3. **Parent-child relationships not showing**
   - Ensure parent names match exactly (case-sensitive)
   - Check that parent exists in the dataset

4. **Data validation errors**
   - Review birth/death year logic
   - Ensure children are born after parents (with reasonable age gap)

## Future Enhancements

Potential improvements for future versions:
- Multiple parent support (both mother and father)
- Sibling relationship visualization
- Photo integration
- GEDCOM file import/export
- Timeline view of family events
- DNA match integration
- Source citation management
- Multi-language support

## Credits

Developed as a comprehensive genealogical tool for the Asher family lineage tracking.

## License

This project is for personal/family use. Feel free to adapt for your own family tree needs.
