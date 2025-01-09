from flask import Flask, request, render_template, jsonify
import dns.resolver

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_dns_records", methods=["POST"])
def get_dns_records():
    website = request.json.get("website")
    dns_records = {}

    # DNS record types to fetch
    record_types = ['A', 'AAAA', 'MX', 'CNAME', 'NS', 'TXT', 'SOA']

    for record_type in record_types:
        try:
            records = dns.resolver.resolve(website, record_type)
            if record_type not in dns_records:
                dns_records[record_type] = []
            for record in records:
                dns_records[record_type].append(record.to_text())
        except dns.resolver.NoAnswer:
            dns_records[record_type] = ['No records found']
        except dns.resolver.NXDOMAIN:
            return jsonify({"error": f"The domain '{website}' does not exist."}), 404
        except Exception as e:
            return jsonify({"error": f"Error fetching {record_type} records: {str(e)}"}), 500

    return jsonify(dns_records)

if __name__ == "__main__":
    app.run(debug=True)
