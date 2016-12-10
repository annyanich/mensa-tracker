from jinja2 import Markup


class Momentjs(object):
    """
    This is a wrapper for the Javascript Momentjs library.  It's
    intended to be used within our web templates to print DateTimes out of
    our database while respecting users' timezones and regional date/time
    formatting conventions).  I copied and pasted it from
    Miguel Grinberg's tutorial:
    http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-dates-and-times

    Example usage: {{ Momentjs(timestamp).format("LLL") }}
    """
    def __init__(self, timestamp):
        """
        :param timestamp: A standard Python DateTime object
        """
        self.timestamp = timestamp

    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>"
                      % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
