---
layout: page
title: "Past News"
title_fr: "Nouvelles passées"
permalink: /past-news/
section: past-news
---
<p class="l-en" lang="en">All digests, by month.</p>
<p class="l-fr" lang="fr">Tous les digests, par mois.</p>
{% assign months = site.posts | group_by_exp: "p", "p.date | date: '%Y-%m'" %}
{% for month in months %}
  {% assign first = month.items | first %}
  {% assign m = first.date | date: "%-m" | minus: 1 %}
  <h2><span class="l-en" lang="en">{{ first.date | date: "%B %Y" }}</span><span class="l-fr" lang="fr">{{ site.fr_months[m] | capitalize }} {{ first.date | date: "%Y" }}</span></h2>
  <ul class="day-list">
  {% for post in month.items %}
    <li><a href="{{ post.url | relative_url }}">{% include ptitle.html p=post %}</a> · {% include count.html n=post.story_count %}</li>
  {% endfor %}
  </ul>
{% endfor %}
