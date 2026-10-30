---
layout: page
title: "Priority topics"
title_fr: "Thèmes prioritaires"
permalink: /topics/
---
<p class="l-en" lang="en">Days whose stories clearly touch one of the team’s three priority topics.</p>
<p class="l-fr" lang="fr">Les jours dont les nouvelles touchent clairement l’un des trois thèmes prioritaires de l’équipe.</p>
{% for topic in site.topics %}
  <h2 id="{{ topic.tag }}"><span class="l-en" lang="en">{{ topic.en }}</span><span class="l-sep" aria-hidden="true"> / </span><span class="l-fr" lang="fr">{{ topic.fr }}</span></h2>
  {% assign tagged = site.tags[topic.tag] %}
  {% if tagged and tagged.size > 0 %}
  <ul class="day-list">
    {% for post in tagged %}
    <li><a href="{{ post.url | relative_url }}">{% include ptitle.html p=post %}</a><br><span class="l-en" lang="en">{{ post.summary }}</span><span class="l-sep" aria-hidden="true"> / </span><span class="l-fr" lang="fr">{{ post.summary_fr | default: post.summary }}</span></li>
    {% endfor %}
  </ul>
  {% else %}
  <p><span class="l-en" lang="en">No digests yet.</span><span class="l-sep" aria-hidden="true"> / </span><span class="l-fr" lang="fr">Aucun digest pour l’instant.</span></p>
  {% endif %}
{% endfor %}
