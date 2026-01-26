---
layout: page
title: 기업분석
permalink: /analysis/
---

# 기업분석 아카이브

가치투자 관점의 심층 기업 분석

---

{% assign analysis_posts = site.posts | where_exp: "post", "post.categories contains 'analysis'" %}

{% if analysis_posts.size > 0 %}
  <ul class="post-list">
    {% for post in analysis_posts %}
      <li>
        <span class="post-meta">{{ post.date | date: "%Y.%m.%d" }}</span>
        <a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
      </li>
    {% endfor %}
  </ul>
{% else %}
  <p>아직 기업분석 포스트가 없습니다.</p>
{% endif %}
