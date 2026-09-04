Brief overview of application:
- Customers can have upload a brand. 
- Customers can post posts and assign it to a particular brand. 
- You can retrieve, create, delete, and edit the brand information. 
    - If you delete a brand, any posts assigned to the brand are deleted as well. 
- Posts have caption texts, which are checked for PII and negative sentiment through AWS Comprehend
    - If a post has PII, it is immediately blocked, and must be manually overridden to be approved. 
    - If a post has negative sentiment, it is immediately set to pending, and must be approved by an employee. 
    - If for whatever reason, AWS Comprehend is down, the applicaiton will default to 'pending'.
    - Caption must be of 20 characters, mostly so it can be a comprehensive sentence instead of just a few emojis. 
- Posts can have images, which are checked for NSFW content through AWS Rekognition
    - If it has NSFW content the image is prevented from being uploaded into the post. 

To run the code:
- please ensure you have docker desktop and docker compose installed. 
- You should be able to run the code with the following command:
docker compose up --build

If you want to run tests, note that I have two test folders.
- I was able to run these commands in the main Project 1 directory:
pytest media_api/tests/post_tests.py
pytest media_api/tests/brand_tests.py