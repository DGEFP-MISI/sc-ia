# Modifications officielles masquées par les conflits

Ces fichiers ont conservé provisoirement la version de recette.
**Examiner les différences avant toute fusion.**

## sites_conformes/templates/sites_conformes_core/standalone.html

[Version recette](https://github.com/DGEFP-MISI/sc-ia/blob/b8f591bc7e0774754c35e1d473586f02ed18b253/sites_conformes/templates/sites_conformes_core/standalone.html) · [Version officielle](https://github.com/numerique-gouv/sites-conformes/blob/579ed6695c3b2545d1f8be2a73a5e1c60067d97d/sites_conformes/templates/sites_conformes_core/standalone.html)

~~~diff
--- /dev/fd/63	2026-11-05 08:37:44.187685721 +0000
+++ /dev/fd/62	2026-11-05 08:37:44.187685721 +0000
@@ -24,10 +24,7 @@
     {% dsfr_favicon %}
 
     {% dsfr_css %}
-    <link href="{% static 'css/style.css' %}" rel="stylesheet" type="text/css" />
-    {% if assistant_ia_enabled %}
-      <link href="{% static 'assistant/assistant.css' %}" rel="stylesheet" type="text/css" />  
-    {% endif %}
+    <link href="{% static 'css/style.css' %}" rel="stylesheet" />
 
     {% block extra_css %}
     {% endblock extra_css %}
@@ -63,15 +60,14 @@
       {% endblock content %}
     </main>
 
-    {% if assistant_ia_enabled %}
-      {% include "assistant/sidebar.html" %}
-    {% endif %}
-
     {% block follow_newsletter_social_media %}
       {% if settings.sites_conformes_core.CmsDsfrConfig.show_newsletter_and_social_block %}
-        <aside id="cmsfr-block-follow">
-          {% include "sites_conformes_core/blocks/follow.html" %}
-        </aside>
+        {% with config=settings.sites_conformes_core.CmsDsfrConfig %}
+          <aside id="cmsfr-block-follow"
+                 aria-label="{% if config.show_newsletter_block and config.show_social_block %}{% translate "Newsletter and social media" %}{% elif config.show_newsletter_block %}{% translate "Newsletter" %}{% else %}{% translate "Social media" %}{% endif %}">
+            {% include "sites_conformes_core/blocks/follow.html" %}
+          </aside>
+        {% endwith %}
       {% endif %}
     {% endblock follow_newsletter_social_media %}
 
@@ -82,9 +78,6 @@
     {% endif %}
 
     {% dsfr_js nonce=request.csp_nonce %}
-    {% if assistant_ia_enabled %}
-      <script src="{% static 'assistant/assistant.js' %}" defer nonce="{{ request.csp_nonce }}"></script>
-    {% endif %}
     {% block extra_js %}
     {% endblock extra_js %}
 
~~~

