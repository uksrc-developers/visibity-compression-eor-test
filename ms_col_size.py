#!/usr/bin/env python3

import os
import click
from casacore import tables

@click.command()
@click.argument('ms_path', type=click.Path(exists=True, file_okay=False))
@click.argument('column_name', type=str)
def get_column_disk_usage(ms_path, column_name):
    """Estimate disk space used by a COLUMN in a Measurement Set (MS_PATH)."""
    tab = tables.table(ms_path, ack=False)
    dm_info = tab.getdminfo()
    
    # Find the DataManager for the column
    for dm in dm_info:
        if column_name in dm_info[dm].get('COLUMNS', []):
            seqnr = dm_info[dm].get('SEQNR', None)
            if seqnr is None:
                raise click.ClickException(f"No SEQNR found for DataManager {dm}.")
            break
    else:
        raise click.ClickException(f"Column '{column_name}' not found in MS.")
    
    total_size = 0
    for suffix in ['', '_TSM0']:
        file_path = os.path.join(ms_path, f'table.f{seqnr}{suffix}')
        if os.path.isfile(file_path):
            total_size += os.path.getsize(file_path)

    click.echo(f"{column_name}: {total_size/1e6:.2f} MB")

if __name__ == '__main__':
    get_column_disk_usage()

