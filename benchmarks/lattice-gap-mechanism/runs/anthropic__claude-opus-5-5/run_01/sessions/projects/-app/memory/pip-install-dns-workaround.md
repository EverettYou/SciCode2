---
name: pip-install-dns-workaround
description: "In this sandbox, pip installs fail because files.pythonhosted.org does not resolve; fix via /etc/hosts mapping to the pypi.org CDN IP"
metadata:
  node_type: memory
  type: reference
  originSessionId: 842364dd-85bc-4fa9-8fea-264336a7a5e5
  modified: 2026-10-29T16:50:14.371Z
---

`pip install X` fails with "Name or service not known" for files.pythonhosted.org, while pypi.org resolves (Fastly CDN, e.g. 151.101.64.223).

Fix that worked (2026-10-29): `IP=$(getent ahosts pypi.org | awk '{print $1}' | head -1); echo "$IP files.pythonhosted.org" >> /etc/hosts` then pip install normally (backup of original hosts at /tmp/hosts.bak during that session).

**How to apply:** do this first whenever a pip install hits a DNS error for files.pythonhosted.org. numba was needed for fast exact-diagonalization kernels; see [[layered-oxide-half-filling-task]].
