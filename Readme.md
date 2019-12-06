# Cloud Nonce Discovery
## Intro
This repository details the use of horizontal scale computing via Amazon Web Services to discover ‘golden nonces’ as known in the blockchain proof of work concept.

## Prerequisites
* Python ≥ 2.7
* AWS CLI
* Keypair

## Build
`python brute_upload.py`

### Parameters

```
parser = argparse.ArgumentParser(
    description=“Run blockchain with difficulty D”,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    “—-log”,
    default=False,
    help=“If we should log files in python script”,
)

parser.add_argument(
    “-—difficulty”,
    default=1,
    type=int,
    help=“Difficulty of nonce discovery”,
)

parser.add_argument(
    “-—time-limit”,
    default=1,
    type=float,
    help=“Maximum time blockchain will run for in ms”,
)

parser.add_argument(
    “—-vms”,
    default=1,
    type=int,
    help="Number of virtual machines to spawn",
)

parser.add_argument(
    "--confidence",
    default=1,
    type=float,
    help="Confidence value",
)
```
