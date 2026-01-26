---
layout: page
title: 전체 아카이브
permalink: /archive/
---

# 전체 아카이브

모든 포스트를 날짜순으로 확인하세요.

---

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}

{% for year in posts_by_year %}
## {{ year.name }}

<ul class="post-list">
  {% for post in year.items %}
    <li>
      <span class="post-meta">{{ post.date | date: "%m.%d" }}</span>
      <a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
      {% if post.categories %}
        <span class="post-categories">
          {% for category in post.categories limit:2 %}
            <span class="category">{{ category }}</span>
          {% endfor %}
        </span>
      {% endif %}
    </li>
  {% endfor %}
</ul>
{% endfor %}

{% if site.posts.size == 0 %}
<p>아직 포스트가 없습니다.</p>
{% endif %}
