#!/usr/bin/env python3

import aws_cdk as cdk

from banseguro.banseguro_stack import BanseguroStack


app = cdk.App()
BanseguroStack(app, "BanseguroStack")

app.synth()
