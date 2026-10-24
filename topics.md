---
layout: page
title: "Thèmes prioritaires / Priority topics"
permalink: /topics/
---
<p><span lang="fr">Les jours dont les nouvelles touchent clairement l’un des trois thèmes prioritaires de l’équipe.</span><br>
<span lang="en">Days whose stories clearly touch one of the team’s three priority topics.</span></p>
{% for topic in site.topics %}
  <h2 id="{{ topic.tag }}"><span lang="fr">{{ topic.fr }}</span> / <span lang="en">{{ topic.en }}</span></h2>
  {% assign tagged = site.tags[topic.tag] %}
  {% if tagged and tagged.size > 0 %}
  <ul class="day-list">
    {% for post in tagged %}
    <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a><br>{{ post.summary }}</li>
    {% endfor %}
  </ul>
  {% else %}
  <p>Aucun digest pour l’instant. / No digests yet.</p>
  {% endif %}
{% endfor %}
