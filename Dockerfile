FROM python:3.9

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# Install requirements
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Create the data directories and set permissions (for SQLite/FAISS)
RUN mkdir -p faiss_index_local && chmod 777 faiss_index_local
RUN touch users.db && chmod 777 users.db

# Expose the port that Hugging Face Spaces expects
EXPOSE 7860

# Start the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
