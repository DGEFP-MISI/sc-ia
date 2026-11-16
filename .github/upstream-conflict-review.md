<!-- markdownlint-disable MD013 -->
# Modifications officielles masquées par les conflits

Ce rapport compare les versions en conflit. Certaines modifications peuvent avoir été intégrées automatiquement.
**Examiner les différences avant toute fusion.**

## config/settings.py

[Version recette](https://github.com/DGEFP-MISI/sc-ia/blob/bf81640e99d00fa29ab08715ad24c39306c71f27/config/settings.py) · [Version officielle](https://github.com/numerique-gouv/sites-conformes/blob/64cd9d88396649a5ebcdb1ac7ba09ca9b9f62804/config/settings.py)

~~~diff
--- version recette
+++ version officielle
@@ -34,6 +34,10 @@
     return value.casefold() in ["1", "true"]
 
 
+def getenv_list(key: str, default: str) -> list[str]:
+    return os.getenv(key, default).replace(" ", "").split(",")
+
+
 # Quick-start development settings - unsuitable for production
 # See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
 
@@ -43,15 +47,7 @@
 # SECURITY WARNING: don't run with debug turned on in production!
 DEBUG = getenv_bool("DEBUG", False)
 
-# Protection des cookies de session et CSRF en production.
-SESSION_COOKIE_SECURE = not DEBUG
-SESSION_COOKIE_HTTPONLY = True
-SESSION_COOKIE_SAMESITE = "Lax"
-
-CSRF_COOKIE_SECURE = not DEBUG
-CSRF_COOKIE_SAMESITE = "Lax"
-
-ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,.localhost").replace(" ", "").split(",")
+ALLOWED_HOSTS = getenv_list("ALLOWED_HOSTS", "127.0.0.1,.localhost")
 USE_X_FORWARDED_HOST = getenv_bool("USE_X_FORWARDED_HOST", False)
 
 HOST_PROTO = os.getenv("HOST_PROTO", "https")
@@ -117,7 +113,6 @@
     "django.contrib.staticfiles",
     "widget_tweaks",
     "dsfr",
-    "portail_1j1s.assistant.apps.AssistantConfig",
     "sites_conformes.customimages",
     "sites_conformes.core",
     "sites_conformes.blog",
@@ -213,7 +208,6 @@
                 "sites_conformes.core.context_processors.skiplinks",
                 "sites_conformes.core.context_processors.mega_menus",
                 "sites_conformes.core.context_processors.iframe",
-                "portail_1j1s.assistant.context_processors.assistant_settings",
             ],
         },
     },
@@ -474,7 +468,7 @@
 
 WAGTAILIMAGES_IMAGE_MODEL = "sites_conformes_customimages.CustomImage"
 WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]
-WAGTAILDOCS_EXTENSIONS = ["pdf", "docx", "odt", "xlsx", "ods", "pptx", "odp", "csv", "txt"]
+WAGTAILDOCS_EXTENSIONS = getenv_list("WAGTAILDOCS_EXTENSIONS", "pdf,docx,odt,xlsx,ods,pptx,odp,csv,txt")
 SF_SCHEME_DEPENDENT_SVGS = getenv_bool("SF_SCHEME_DEPENDENT_SVGS", False)
 
 # Allows for complex Streamfields without completely removing checks
~~~

