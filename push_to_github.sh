#!/bin/bash
# Script to push to GitHub - just provide your repo URL

echo "🌿 Herbal Plant Detection - GitHub Push Script"
echo "=============================================="
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "✓ Remote 'origin' already configured"
    REMOTE_URL=$(git remote get-url origin)
    echo "  URL: $REMOTE_URL"
    echo ""
    read -p "Push to this remote? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Cancelled."
        exit 0
    fi
else
    echo "No GitHub remote configured yet."
    echo ""
    echo "Please provide your GitHub repository URL"
    echo "Example: https://github.com/username/herbal-plant-detection.git"
    echo "Or: git@github.com:username/herbal-plant-detection.git"
    echo ""
    read -p "Enter GitHub repository URL: " repo_url
    
    if [ -z "$repo_url" ]; then
        echo "❌ No URL provided. Exiting."
        exit 1
    fi
    
    echo ""
    echo "Adding remote 'origin'..."
    git remote add origin "$repo_url"
    echo "✓ Remote added"
    echo ""
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo ""

if git push -u origin "$CURRENT_BRANCH"; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    REMOTE_URL=$(git remote get-url origin)
    # Extract username/repo from URL
    if [[ $REMOTE_URL =~ github.com[:/]([^/]+)/([^/]+)\.git ]]; then
        USERNAME="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        echo "📦 View your repository at:"
        echo "   https://github.com/$USERNAME/$REPO"
    fi
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "1. Repository doesn't exist on GitHub - create it first at https://github.com/new"
    echo "2. Authentication required - you may need to set up SSH keys or use a token"
    echo "3. Wrong URL - check your repository URL"
    echo ""
    echo "For HTTPS, you may need a Personal Access Token instead of password"
    exit 1
fi

