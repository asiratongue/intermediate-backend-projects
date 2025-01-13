

create  a seperate feature for querying based on metadata?


image = models.ImageField(upload_to='images/')

# These are automatically available:
image.name          # The filename
image.path          # Full filesystem path
image.size          # File size in bytes
image.url           # URL to access the image
image.width         # Image width in pixels
image.height        # Image height in pixels
image.content_type  # The MIME type (e.g., 'image/jpeg') 


TODO:

implement aws cloud storage,
Implement rate limiting,
implement either caching transformed images or message queue,
implement:
#### Retrieve an image:

```
GET /images/:id
```

Response should be the image actual image detail.

#### Get a paginated list of images:

```
GET /images?page=1&limit=10
```

error handle + write tests,
git push + write docs