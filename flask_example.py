from flask import jsonify, request, Blueprint
from models import db, Blog, User # Make sure to import your db instance and models

bp = Blueprint('blogs', __name__, url_prefix='/blogs')

## --- Routes for the Blog Collection ---

# [GET] /blogs - Get all blogs
# [POST] /blogs - Create a new blog
@bp.route('', methods=['GET', 'POST'])
def handle_blogs():
    # Get all blogs 📝
    if request.method == 'GET':
        # SQLAlchemy query to get all blogs
        all_blogs = db.session.execute(db.select(Blog).order_by(Blog.id.desc())).scalars().all()
        
        # Format the blog objects into a list of dictionaries
        results = [blog.to_dict() for blog in all_blogs]
        
        return jsonify(results), 200

    # Create a new blog ✍️
    if request.method == 'POST':
        # Get data from the request body (sent by the frontend)
        data = request.get_json()
        if not data or not data.get('title') or not data.get('content') or not data.get('user_id'):
            return jsonify({'error': 'Missing data. Title, content, and user_id are required.'}), 400

        # Optional: Check if the user exists
        user = db.session.get(User, data['user_id'])
        if not user:
            return jsonify({'error': 'User not found.'}), 404

        # Create a new Blog instance
        new_blog = Blog(
            title=data['title'],
            content=data['content'],
            user_id=data['user_id']
        )
        
        # Add to the database session and commit
        db.session.add(new_blog)
        db.session.commit()
        
        return jsonify(new_blog.to_dict()), 201 # 201 Created status


## --- Routes for a Specific Blog ---

# [GET] /blogs/<blog_id> - Get a single blog
# [PUT] /blogs/<blog_id> - Update a blog
# [DELETE] /blogs/<blog_id> - Delete a blog
@bp.route('/<int:blog_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_blog(blog_id):
    # SQLAlchemy query to get the specific blog by its ID
    blog = db.session.get(Blog, blog_id)
    if blog is None:
        return jsonify({'error': 'Blog not found.'}), 404

    # View a specific blog 📄
    if request.method == 'GET':
        return jsonify(blog.to_dict()), 200

    # Update a blog 🔄
    if request.method == 'PUT':
        data = request.get_json()
        # Update fields if they exist in the request data
        blog.title = data.get('title', blog.title)
        blog.content = data.get('content', blog.content)
        
        # Commit the changes to the database
        db.session.commit()
        
        return jsonify(blog.to_dict()), 200

    # Delete a blog 🗑️
    if request.method == 'DELETE':
        # Optional: Add logic here to ensure only an admin or the blog's author can delete it
        
        # Delete the blog from the database
        db.session.delete(blog)
        db.session.commit()
        
        return jsonify({'message': f'Blog with ID {blog_id} deleted successfully.'}), 200
