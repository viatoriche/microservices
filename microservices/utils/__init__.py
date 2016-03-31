def get_template_source(jinja_env, template_name):
    return jinja_env.loader.get_source(jinja_env, template_name)[0]


def get_all_variables_from_template(jinja_env, template_name):
    from jinja2 import meta
    template_source = get_template_source(jinja_env, template_name)
    parsed_content = jinja_env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)


def set_logging(level='DEBUG', log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):

    import logging
    import os

    logging.basicConfig(
        level=getattr(logging, os.environ.get('LOG_LEVEL', level)),
        format=log_format,
    )


def get_logger(name=__name__):
    import logging
    return logging.getLogger(name)