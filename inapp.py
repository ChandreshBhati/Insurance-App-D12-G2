from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Run the app
    port = 5001  # You can change this to any port you prefer
    print(f"Application running on port {port}")
    app.run(debug=True, port=port)