import copy

from django.template import context as django_context


def _compat_base_context_copy(self):
    """Compatibility shim for Django BaseContext copying under newer Python runtimes."""
    duplicate = self.__class__()
    duplicate.dicts = self.dicts[:]
    return duplicate


def _compat_context_copy(self):
    """Compatibility shim for Django Context copying under newer Python runtimes."""
    duplicate = self.__class__(self.dicts[0] if self.dicts else None, autoescape=self.autoescape, use_l10n=self.use_l10n, use_tz=self.use_tz)
    duplicate.dicts = self.dicts[:]
    duplicate.render_context = copy.copy(self.render_context)
    duplicate.template_name = self.template_name
    duplicate.template = self.template
    return duplicate


if not getattr(django_context.BaseContext.__copy__, '__name__', '') == '_compat_base_context_copy':
    django_context.BaseContext.__copy__ = _compat_base_context_copy

if not getattr(django_context.Context.__copy__, '__name__', '') == '_compat_context_copy':
    django_context.Context.__copy__ = _compat_context_copy
