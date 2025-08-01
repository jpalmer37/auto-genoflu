import os 
from glob import glob 
from typing import List
import re
import logging
import json
from typing import Callable

def _rename_seqs(rename_fn: Callable, input_path: str, output_path: str) -> None:

    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        
        for line in infile.readlines():
            if line.startswith(">"):
                new_header = rename_fn(line.rstrip().lstrip(">"))
                outfile.write(f">{new_header}\n")
            else:
                outfile.write(line)

def _rename_cfia(fasta_header: str) -> str: 
    new_header = fasta_header
    if "_" in fasta_header: 
        fields = fasta_header.split("_")
        fields[-1] = fields[-1].replace("M", "MP")
        new_header = "_".join(fields)
    return new_header

def _rename_gisaid(fasta_header: str) -> str: 
    fields = fasta_header.split("|")
    new_header = fasta_header + "_" + fields[-3]
    return new_header

def rename_fasta_headers(input_path: str, output_path: str) -> None:
    """
    Rename the headers of a FASTA file.

    Args:
        input_path (str): Path to the input FASTA file.
        output_path (str): Path to the output FASTA file.

    Returns:
        None
    """
    fn_dict = {'cfia': _rename_cfia, 'gisaid': _rename_gisaid}

    file_name = os.path.basename(input_path)
    count = file_name.count("_") + file_name.count("-")

    if count > 6 and file_name.endswith('.consensus.fasta'):
        logging.debug(json.dumps({"event_type": "renaming_cfia_headers", "file_name": file_name}))
        _rename_seqs(fn_dict['cfia'], input_path, output_path)
    
    elif re.search("EPI[-_]ISL", file_name, flags=re.IGNORECASE):
        logging.debug(json.dumps({"event_type": "renaming_gisaid_headers", "file_name": file_name}))
        _rename_seqs(fn_dict['gisaid'], input_path, output_path)
    else:
        logging.warning(json.dumps({"event_type": "unknown_file_type_detected", "file_name": file_name}))
        _rename_seqs(fn_dict['cfia'], input_path, output_path)
    
    

