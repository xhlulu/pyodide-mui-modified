from functools import partial
import datetime
import js
import pyodide
import js.MaterialUI as mui
import js.React.createElement as e


def jsobj(**kwargs):
    return js.Object.fromEntries(pyodide.to_js(kwargs))


def __to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def pythonify(component):
    """
    Makes a react component feel like you are calling a function
    """

    def aux(self, old_args, old_kwargs, *args, **kwargs):
        kwargs = {__to_camel_case(k): v for k, v in kwargs.items()}
        if old_args is None:
            old_args = []
        if old_kwargs is None:
            old_kwargs = {}

        old_args.extend(args)
        old_kwargs.update(kwargs)

        args = old_args
        kwargs = old_kwargs

        rc = js.React.createElement(component, jsobj(**kwargs), *args)
        rc.update = partial(aux.__get__(rc, rc.__class__), args, kwargs)

        return rc

    return partial(aux, component, None, None)


Typography = pythonify(mui.Typography)
Link = pythonify(mui.Link)
Container = pythonify(mui.Container)
ThemeProvider = pythonify(mui.ThemeProvider)
CssBaseline = pythonify(mui.CssBaseline)
SvgIcon = pythonify(mui.SvgIcon)
div = pythonify("div")
path = pythonify("path")


@mui.makeStyles
def use_styles(theme):
    return jsobj(
        root=jsobj(margin=theme.spacing(6, 0, 3)),
        light_bulb=jsobj(verticalAlign="middle", marginRight=theme.spacing(1)),
    )


theme = mui.createTheme(
    dict(
        palette=dict(
            primary=dict(main="#556cd6"),
            secondary=dict(main="#19857b"),
            error=dict(main="#FF1744"),
            background=dict(default="#fff"),
        )
    )
)


@pythonify
def LightBulbIcon(props, children):
    return SvgIcon(
        path(
            d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"
        ),
        **props.to_py(),
    )


@pythonify
def ProTip(props, children):
    classes = use_styles()
    return Typography(class_name=classes.root, color="textSecondary").update(
        LightBulbIcon(class_name=classes.light_bulb),
        "Pro tip: See more ",
        Link(
            "templates",
            href="https://material-ui.com/getting-started/templates/",
        ),
        " on the Material-UI documentation.",
    )


@pythonify
def Copyright(props, children):
    return Typography(variant="body2", color="textSecondary", align="center").update(
        "Copyright © ",
        Link(
            "Your Website",
            href="https://material-ui.com/",
            color="inherit",
        ),
        f" {datetime.datetime.now().year}.",
    )


@pythonify
def App(props, children):
    return Container(maxWidth="sm").update(
        div(
            Typography(
                "CDN v4-beta example",
                variant="h4",
                component="h1",
                gutter_bottom=True,
            ),
            ProTip(),
            Copyright(),
            style=dict(marginTop=24),
        ),
    )


# Create a div to contain our component and render our App
dom_container = js.document.createElement("div")
js.document.body.appendChild(dom_container)
js.ReactDOM.render(
    ThemeProvider(CssBaseline(), App(), theme=theme),
    dom_container,
)
