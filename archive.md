---
layout: page
title: "Archives / Archive"
permalink: /archive/
---
<p><span lang="fr">Tous les digests, par mois.</span> / <span lang="en">All digests, by month.</span></p>
{% assign months = site.posts | group_by_exp: "p", "p.date | date: '%Y-%m'" %}
{% for month in months %}
  {% assign first = month.items | first %}
  {% assign m = first.date | date: "%-m" | minus: 1 %}
  <h2>{{ site.fr_months[m] | capitalize }} {{ first.date | date: "%Y" }} / {{ first.date | date: "%B %Y" }}</h2>
  <ul class="day-list">
  {% for post in month.items %}
    <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> · {{ post.story_count }} nouvelles / stories</li>
  {% endfor %}
  </ul>
{% endfor %}
