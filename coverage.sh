#!/bin/bash

# Set up error handling
set -e

# Ensure virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Directories for the two projects
ADMIN_API_DIR="admin_api"
FRONTEND_API_DIR="frontend_api"

# Ensure coverage and pytest are installed
pip install pytest pytest-cov coverage

# Function to run tests and generate coverage for a project
run_project_coverage() {
    local project_dir=$1
    local project_name=$2

    echo "Running tests and generating coverage for $project_name..."
    
    cd "$project_dir"
    
    # Run pytest with coverage
    pytest --cov=. --cov-report=xml:../coverage-$project_name.xml
    
    cd ..
}

# Clean up previous coverage files
rm -f .coverage* coverage*.xml combined_coverage.xml combined_coverage.html

# Run tests and generate coverage for each project
run_project_coverage "$ADMIN_API_DIR" "admin_api"
run_project_coverage "$FRONTEND_API_DIR" "frontend_api"

# Combine coverage reports
echo "Combining coverage reports..."
coverage combine \
    "$ADMIN_API_DIR/.coverage" \
    "$FRONTEND_API_DIR/.coverage"

# Generate combined reports
coverage report --skip-covered
coverage html -d combined_coverage_html
coverage xml -o combined_coverage.xml

# Optional: Open HTML report
if command -v xdg-open &> /dev/null; then
    xdg-open combined_coverage_html/index.html
elif command -v open &> /dev/null; then
    open combined_coverage_html/index.html
else
    echo "Combined coverage report generated in combined_coverage_html/index.html"
fi

echo "Coverage report generation complete."