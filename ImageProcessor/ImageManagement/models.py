from django.db import models
from django.contrib.auth.models import User
from .storage import MediaStorage

class ImageModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="Images/", storage=MediaStorage()) 
    created_at = models.DateTimeField(auto_now_add=True)

    IMAGE_TYPE = [
       ('source', 'Source Image'),
       ('edited', 'Edited Image')
   ]
    type = models.CharField(max_length=10, choices=IMAGE_TYPE,default='source')
    source_image = models.ForeignKey('self',null=True, blank=True,on_delete=models.CASCADE,related_name='edits')

    @property
    def is_edited(self):
        return self.type == 'edited'

    def __str__(self):
        return self.size


