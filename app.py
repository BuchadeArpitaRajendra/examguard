from flask import Flask

# Create Flask application instance
app = Flask(__name__)

# Define a route for the homepage
@app.route('/')
def home():
    return 'Hello, Welcome to ExamGuard!'

# Define a route for testing
@app.route('/test')
def test():
    return 'Flask is working correctly!'

# Run the application
if __name__ == '__main__':
    app.run(debug=True)