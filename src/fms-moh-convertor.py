from pathlib import PurePath
from io import StringIO
import sys
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

    log_path = output.with_name(output.stem + ".log")

    print(manifest)
    print(output)
    print(log_path)

    conversion = MOHSampleManifestConversion(
        manifest, fms_template_file_path, output
    )
    try:
        conversion.do_conversion()
    except Exception as e:
        # Capture any exception so that we can still write the log file
        sys.stderr.write('Conversion failed')
        sys.stderr.write(str(e))
    finally:
        # Write log no matter what happens, since we capture exception
        # messages in the log
        conversion.log.output_messages()
        # Write log file
        with open(log_path, "w", encoding="utf-8") as log_file:
            conversion.log.write_log(log_file)
           
    print("DONE")




cli.add_command(convert)

if __name__ == '__main__':
    cli()
