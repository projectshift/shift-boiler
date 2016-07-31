# Two versions of recaptcha
--------

You have an option to either use newer recaptcha v2 supplied by wtforms, or
if its not customizable enough, use our fallback v1 vesion with custom themes.

To use v1 just include custom field template:

```
{% include 'recaptcha/v1.j2' %}

To use recaptcha v2 render it in normally:

```
{{ form.recaptcha() }}
<div class="errors">{% for error in form.errors.recaptcha %}<span>{{ error }}</span><br>{% endfor %}</div>
```

Alternatively include filed template as we do with v1:

```

# render v.1
{% include 'recaptcha/v1.j2' %}

# or version 2
{% include 'recaptcha/v2.j2' %}

```





