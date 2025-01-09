from flask import Flask, request, render_template, jsonify
import dns.resolver

app = Flask(__name__)

# Create a custom DNS resolver and set a timeout
resolver = dns.resolver.Resolver()
resolver.timeout = 10  # Timeout in seconds
resolver.lifetime = 15  # Total time before considering the query failed

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_dns_records", methods=["POST"])
def get_dns_records():
    website = request.json.get("website")
    if not website:
        return jsonify({"error": "No website provided"}), 400

    dns_records = {}
    record_types = ['A', 'AAAA', 'MX', 'CNAME', 'NS', 'TXT', 'SOA']

    # Fetch the DNS records for each type using the custom resolver
    for record_type in record_types:
        try:
            records = resolver.resolve(website, record_type)
            dns_records[record_type] = [record.to_text() for record in records]
        except dns.resolver.NoAnswer:
            dns_records[record_type] = ['No records found']
        except dns.resolver.NXDOMAIN:
            return jsonify({"error": f"The domain '{website}' does not exist."}), 404
        except dns.resolver.Timeout:
            dns_records[record_type] = ['Query timed out']
        except Exception as e:
            dns_records[record_type] = [f"Error: {str(e)}"]

    return jsonify(dns_records)

if __name__ == "__main__":
    app.run(debug=True)
