import os
import datetime
from flask import Flask, redirect, render_template_string, request, send_from_directory, url_for, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ફાઇલોનો ડેટા સ્ટોર કરવા માટે
files_info = []

BRANCH_IPS = [
    {"branch": "મામલતદાર ટેબલ", "ip": "192.168.1.10"},
    {"branch": "જન સેવા કેન્દ્ર", "ip": "192.168.1.11"},
    {"branch": "ઈ-ધરા શાખા", "ip": "192.168.1.12"},
    {"branch": "મહેસૂલ શાખા", "ip": "192.168.1.13"},
    {"branch": "પુરવઠા શાખા", "ip": "192.168.1.14"},
    {"branch": "ચૂંટણી શાખા", "ip": "192.168.1.15"},
    {"branch": "Estate", "ip": "192.168.1.16"},
    {"branch": "Sahay", "ip": "192.168.1.17"},
    {"branch": "Jamin 1", "ip": "192.168.1.18"},
    {"branch": "Jamin 2", "ip": "192.168.1.19"},
    {"branch": "Circle (સર્કલ)", "ip": "192.168.1.20"},
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mamlatdar Kacheri Sutrapada - File Transfer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header-bg {
            background: linear-gradient(135deg, #0d6efd, #0a58ca);
            color: white;
            padding: 20px 0;
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        .card { border: none; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 20px; }
        .footer { text-align: center; margin-top: 40px; padding: 15px; color: #6c757d; font-size: 14px; }
        .developer-tag { font-weight: bold; color: #0d6efd; }
    </style>
</head>
<body>

    <div class="header-bg text-center">
        <h2>🏛️ મામલતદાર કચેરી, સુત્રાપાડા</h2>
        <p class="mb-0">All Branches File Sharing Dashboard</p>
    </div>

    <div class="container my-4">
        <div class="row">
            
            <div class="col-md-8">
                <div class="card p-4">
                    <h5 class="card-title text-primary mb-3">📤 ફાઇલ મોકલો (Send File)</h5>
                    <form method="post" enctype="multipart/form-data">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label font-weight-bold">ક્યાંથી મોકલો છો? (From):</label>
                                <select class="form-select" name="from_branch" required>
                                    <option value="" selected disabled>તમારી બ્રાન્ચ પસંદ કરો</option>
                                    {% for pc in branch_ips %}
                                        <option value="{{ pc.branch }}">{{ pc.branch }}</option>
                                    {% endfor %}
                                </select>
                            </div>

                            <div class="col-md-6">
                                <label class="form-label font-weight-bold text-danger">કોને મોકલવી છે? (To):</label>
                                <select class="form-select" id="to_branch_select" name="to_branch" required>
                                    <option value="" selected disabled>સામેવાળી બ્રાન્ચ પસંદ કરો</option>
                                    <option value="બધા માટે (All PCs)">📢 બધા માટે (All PCs)</option>
                                    {% for pc in branch_ips %}
                                        <option value="{{ pc.branch }}">{{ pc.branch }}</option>
                                    {% endfor %}
                                </select>
                            </div>

                            <div class="col-md-8">
                                <label class="form-label">ફાઇલ સિલેક્ટ કરો:</label>
                                <input class="form-control" type="file" name="file" required>
                            </div>

                            <div class="col-md-4 d-flex align-items-end">
                                <button type="submit" class="btn btn-primary w-100">Send File 🚀</button>
                            </div>
                        </div>
                    </form>
                </div>

                <div class="card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="card-title text-success m-0">📁 ફાઇલોની વિગત (Logs)</h5>
                        <button onclick="requestNotificationPermission()" class="btn btn-sm btn-outline-primary">🔔 Enable Notifications</button>
                    </div>
                    
                    <div class="table-responsive">
                        <table class="table table-hover align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th>From</th>
                                    <th>To</th>
                                    <th>File Name</th>
                                    <th>Time</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="file-list-body">
                                {% for item in files_data %}
                                    <tr>
                                        <td><span class="badge bg-secondary">{{ item.from_branch }}</span></td>
                                        <td><span class="badge bg-danger">{{ item.to_branch }}</span></td>
                                        <td>📄 {{ item.filename }}</td>
                                        <td><small class="text-muted">{{ item.time }}</small></td>
                                        <td>
                                            <a href="{{ url_for('download_file', name=item.filename) }}" class="btn btn-sm btn-outline-success">Download</a>
                                        </td>
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card p-3">
                    <h6 class="text-dark mb-3">💻 કચેરીના તમામ PC / IP લિસ્ટ</h6>
                    <ul class="list-group list-group-flush small">
                        {% for pc in branch_ips %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span>{{ pc.branch }}</span>
                                <span class="badge bg-light text-dark border">{{ pc.ip }}</span>
                            </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>

        </div>
    </div>

    <div class="footer">
        <p>મામલતદાર કચેરી સુત્રાપાડા - ડિજિટલ ફાઇલ ટ્રાન્સફર સિસ્ટમ</p>
        <p>Created by: <span class="developer-tag">Paras Bhola</span></p>
    </div>

    <script>
        let lastFileCount = {{ files_data|length }};

        // નોટિફિકેશન ચાલુ કરવાની પરમિશન માંગવી
        function requestNotificationPermission() {
            if ("Notification" in window) {
                Notification.requestPermission().then(permission => {
                    if (permission === "granted") {
                        alert("પોપ-અપ નોટિફિકેશન સફળતાપૂર્વક ચાલુ થઈ ગયા છે!");
                    }
                });
            }
        }

        // નવી ફાઈલ આવે ત્યારે પોપ-અપ મેસેજ બતાવવો
        function showNotification(fromBranch, toBranch, filename) {
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification("📥 નવી ફાઈલ આવી છે!", {
                    body: `From: ${fromBranch}\nTo: ${toBranch}\nFile: ${filename}`,
                    icon: "https://cdn-icons-png.flaticon.com/512/724/724715.png"
                });
            }
        }

        // 3 સેકન્ડે ચેક કરવું કે નવી ફાઈલ આવી છે કે નહીં
        setInterval(() => {
            fetch('/check-new-files')
                .then(response => response.json())
                .then(data => {
                    if (data.length > lastFileCount) {
                        let latestFile = data[0]; // સૌથી નવી ફાઈલ
                        showNotification(latestFile.from_branch, latestFile.to_branch, latestFile.filename);
                        lastFileCount = data.length;
                        location.reload(); // પેજ રીફ્રેશ કરીને લિસ્ટ અપડેટ કરવું
                    }
                });
        }, 3000);
    </script>

</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        from_branch = request.form.get('from_branch', 'Unknown')
        to_branch = request.form.get('to_branch', 'All PCs')
        
        if file.filename == '':
            return redirect(request.url)
            
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            file_entry = {
                'filename': filename,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'time': datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
            }
            files_info.insert(0, file_entry)
            return redirect(url_for('upload_file'))
    
    return render_template_string(HTML_TEMPLATE, files_data=files_info, branch_ips=BRANCH_IPS)

@app.route('/check-new-files')
def check_new_files():
    return jsonify(files_info)

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)