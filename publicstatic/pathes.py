"""Pathes produced from constants and some other stuff."""

import os.path
from publicstatic import conf
from publicstatic import const


def append(path, *suffix):
    """Append optional suffix to the path."""
    return path if not suffix else os.path.join(path, *suffix)


def site(*suffix):
    """Returns site source directory."""
    return append(os.path.dirname(conf.path()), *suffix)


def package(*suffix):
    """Absolute path to the package directory."""
    return append(os.path.dirname(os.path.abspath(__file__)), *suffix)


def proto(*suffix):
    """Returns full path to the site prototype directory."""
    return append(package(const.PROTO_DIR), *suffix)


def assets(*suffix):
    """Absolute path to assets directory inside site source directory."""
    return site(const.ASSETS_DIR, *suffix)


def pages(*suffix):
    return site(const.PAGES_DIR, *suffix)


def posts(*suffix):
    return site(const.POSTS_DIR, *suffix)


def data(*suffix):
    return site(const.DATA_DIR, *suffix)


def templates(*suffix):
    """Absolute path to templates inside site source directory."""
    return site(const.TEMPLATES_DIR, *suffix)


def theme(*suffix):
    """Absolute path to theme directory inside site source directory
    or in the theme package if the theme is not installed to the site
    source."""
    installed = os.path.isdir(site(const.THEME_DIR))
    return (theme_installed if installed else theme_source)(*suffix)


def theme_source(*suffix):
    """Absolute path to theme directory inside in the theme package."""
    # TODO: Use package name
    return package(*suffix)


def theme_installed(*suffix):
    """Absolute path to theme directory inside in the theme package."""
    return site(const.THEME_DIR, *suffix)


def theme_assets(*suffix):
    """Absolute path to theme assets directory."""
    return theme(const.ASSETS_DIR, *suffix)


def theme_assets_source(*suffix):
    """Absolute path to package theme assets directory."""
    return theme_source(const.ASSETS_DIR, *suffix)


def theme_assets_installed(*suffix):
    """Absolute path to site theme assets directory."""
    return theme_installed(const.ASSETS_DIR, *suffix)


def theme_templates(*suffix):
    """Absolute path to theme templates directory."""
    return theme(const.TEMPLATES_DIR, *suffix)


def theme_templates_source(*suffix):
    """Absolute path to theme templates directory."""
    return theme_source(const.TEMPLATES_DIR, *suffix)


def theme_templates_installed(*suffix):
    """Absolute path to theme templates directory."""
    return theme_installed(const.TEMPLATES_DIR, *suffix)
