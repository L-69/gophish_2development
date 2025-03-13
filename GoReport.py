#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 3rd Party Libraries
import click
from gophish import Gophish
# Goreport Libraries
from lib import banners, goreport


# Setup an AliasedGroup for CLICK
class AliasedGroup(click.Group):
    """Allows commands to be called by their first unique character."""

    def get_command(self, ctx, cmd_name):
        """
        Allows commands to be called by their first unique character
        :param ctx: Context information from click
        :param cmd_name: Calling command name
        :return:
        """
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


# Create the help option for CLICK
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def GoReport():
    """Everything starts here."""
    pass


# Setup our CLICK arguments and help text
@GoReport.command(name='report', short_help="Generate a full report for the selected campaign \
-- either CSV or DOCX.")
@click.option('--id', type=click.STRING, is_flag=False, help="The target campaign's ID. You can \
provide a comma-separated list of IDs (e.g. -id #,#,#).", required=True)
@click.option('--format', type=click.Choice(['excel', 'word', 'quick']), help="Use this option to \
choose between report formats.", required=True)
@click.option('--combine', is_flag=True, help="Combine all results into one report. The first \
campaign ID will be used for information such as campaign name, dates, and URL.", required=False)
@click.option('--complete', is_flag=True, help="Optionally mark the campaign as complete in \
Gophish.", required=False)
@click.option('--config', type=click.Path(exists=True, readable=True, resolve_path=True),
              help="Name an alternate config file for GoReport to use. The default is \
gophish.config.")
@click.option('-g', '--google', is_flag=True, help="Enables using the Google Maps Geolocate API \
to match Gophish event coordinates with an address. Requires a Geolocate API key in \
the config file.", required=False)
@click.option('-v', '--verbose', is_flag=True, help="Sets verbose to true so GoReport will \
display some additional feedback, such as flagging IP mis-matches.", required=False)
@click.pass_context
def parse_options(self, id, format, combine, complete, config, google, verbose):
    """GoReport uses the Gophish API to connect to your Gophish instance using the
    IP address, port, and API key for your installation. This information is provided
    in the gophish.config file and loaded at runtime. GoReport will collect details
    for the specified campaign and output statistics and interesting data for you.

    Select campaign ID(s) to target and then select a report format.\n
       * csv: A comma separated file. Good for copy/pasting into other documents.\n
       * word: A formatted docx file. A template.docx file is required (see the README).\n
       * quick: Command line output of some basic stats. Good for a quick check or client call.\n
    """
    # Print the Gophish banner
    banners.print_banner()
    # Create a new Goreport object that will use the specified report format
    gophish = goreport.Goreport(format, config, google, verbose)
    # Execute reporting for the provided list of IDs
    gophish.run(id, combine, complete)


if __name__ == '__main__':
    parse_options()
