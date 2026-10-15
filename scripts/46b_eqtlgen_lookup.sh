# Query eQTLGen for rs6920220
echo "=== eQTLGen lookup for rs6920220 ==="
curl -sS "https://molgenis26.gcc.rug.nl/downloads/eqtlgen/cis-eqtl/2019-12-11-cis-eQTLsFDR-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz" \
  -o /tmp/eqtlgen_cis.gz 2>/dev/null &
CURL_PID=$!

# While that's downloading (it's ~300 MB), query the summary API
curl -sS "https://eqtlgen.org/api/v1/eqtl?rsid=rs6920220" 2>/dev/null | head -50 || \
  echo "API not available - need to download the full file (300 MB)"

kill $CURL_PID 2>/dev/null
