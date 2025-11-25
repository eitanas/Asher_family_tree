#!/bin/bash

# Script to push your Asher Family Tree to GitHub
# Run this after creating your GitHub repository

echo "📦 Pushing Asher Family Tree to GitHub..."
echo ""
echo "Please enter your GitHub username:"
read GITHUB_USERNAME

echo ""
echo "Setting up GitHub remote..."
git remote add origin https://github.com/$GITHUB_USERNAME/asher-family-tree.git

echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Success! Your code is now on GitHub!"
echo ""
echo "Next steps:"
echo "1. Go to https://share.streamlit.io/"
echo "2. Sign in with GitHub"
echo "3. Deploy your app following the instructions in DEPLOYMENT_INSTRUCTIONS.md"
echo ""
echo "Your repository: https://github.com/$GITHUB_USERNAME/asher-family-tree"
