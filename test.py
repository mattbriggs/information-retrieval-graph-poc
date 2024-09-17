import yaml

with open ("working/fowler.yml", "r") as stream:
    config = yaml.safe_load(stream)

print(config)