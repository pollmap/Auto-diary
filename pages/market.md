---
layout: page
title: 시황 브리핑
permalink: /market/
---

# 시황 브리핑 아카이브

매일 오전 6시, 글로벌 금융 시장을 한눈에.

---

{% assign market_posts = site.posts | where_exp: "post", "post.categories contains 'market'" %}

{% if market_posts.size > 0 %}
  <ul class="post-list">
    {% for post in market_posts %}
      <li>
        <span class="post-meta">{{ post.date | date: "%Y.%m.%d" }}</span>
        <a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
      </li>
    {% endfor %}
  </ul>
{% else %}
  <p>아직 시황 브리핑이 없습니다. 곧 자동으로 발행됩니다.</p>
{% endif %}
