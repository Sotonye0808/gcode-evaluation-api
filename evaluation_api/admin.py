"""
Admin configuration for the Evaluation API.

Since this API is stateless and doesn't have persistent models,
this admin configuration is minimal and primarily used for 
service monitoring and configuration if needed in the future.
"""

from django.contrib import admin

# Since this is a stateless evaluation API with no models,
# there are no model admins to register.
# This file is kept for future extensibility.

# Optional: Custom admin site configuration
admin.site.site_header = "GCode Evaluation API Admin"
admin.site.site_title = "Evaluation API"
admin.site.index_title = "Evaluation API Administration"
