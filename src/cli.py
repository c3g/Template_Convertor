from pathlib import PurePath
import click
from moh.sample_manifest_conversion import MOHSampleManifestConversion

# Command line interface
#
# -m : sample manifest file path
# -o : output file path (optional)

# Path to the empty fms template
fms_template_file_path = PurePath("config/fms_sample_submission_template.xlsx")

@click.group()
def cli():
    pass

@click.command()
@click.argument('manifest_file_path', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True))
@click.option('--output_path', type=click.Path(dir_okay=False, writable=True, resolve_path=True), help="The path to the output file to create")
def convert(manifest_file_path, output_path):
    manifest = PurePath(manifest_file_path)

    if output_path is None:
        manifest_name = manifest.stem
        output_file_name = manifest_name + ".fms.xlsx"
        output = manifest.with_name(output_file_name)
    else:
        output = PurePath(output_path)

    log = output.with_name(output.stem + ".log")

    print(manifest)
    print(output)
    print(log)

    conversion = MOHSampleManifestConversion(
        manifest, fms_template_file_path, output, log
    )
    conversion.do_conversion()

    print("DONE")




cli.add_command(convert)

if __name__ == '__main__':
    cli()

