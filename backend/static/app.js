const API = "http://127.0.0.1:5000/api"

function authHeaders() {
  const token = localStorage.getItem("token")
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  }
}

Vue.createApp({
  data() {
    return {
      loggedIn:      false,
      loading:       false,
      authTab:       "login",
      authError:     "",
      authSuccess:   "",
      currentUser:   {},
      adminTab:      "dashboard",
      companyTab:    "dashboard",
      studentTab:    "dashboard",
      stats:         {},
      companies:     [],
      students:      [],
      drives:        [],
      applications:  [],
      exportMessage: "",
      companySearch: "",
      studentSearch: "",
      companyStats:      {},
      companyDrives:     [],
      driveApplications: [],
      studentStats:       {},
      studentDrives:      [],
      studentApplications:[],
      placementHistory: [],
      driveSearch:        "",
      selectedResume: null,
      uploadMessage: "",
      showEditStudentProfile: false,
      editStudentForm: {
        full_name: "", roll_number: "", branch: "", department: "",
        cgpa: "", year: "", phone: "", skills: ""
      },
      selectedDrive:     null,
      showCreateDrive:   false,
      showEditProfile: false,
      editProfileForm: {
        company_name: "", industry: "", location: "",
        website: "", hr_contact_name: "", hr_contact_email: "", description: ""
      },
      driveError:        "",
      driveForm: {
        drive_name: "", job_title: "", job_description: "",
        eligibility_branch: "", eligibility_cgpa: "", eligibility_year: "",
        salary: "", location: "", application_deadline: "", interview_type: "In-person"
      },
      loginForm:     { username: "", password: "" },
      registerForm:  {
        role: "student", username: "", email: "", password: "",
        full_name: "", branch: "", cgpa: "", year: "",
        company_name: "", industry: "", location: ""
      }
    }
  },


  mounted() {
    const token = localStorage.getItem("token")
    const user  = localStorage.getItem("user")
    if (token && user) {
      this.currentUser = JSON.parse(user)
      this.loggedIn    = true
      if (this.currentUser.role === "admin")   this.loadDashboard()
      if (this.currentUser.role === "company") this.loadCompanyDashboard()
      if (this.currentUser.role === "student") this.loadStudentDashboard()
    }
  },

  methods: {
    async doLogin() {
      this.authError = ""
      this.loading   = true
      try {
        const res  = await fetch(`${API}/auth/login`, {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(this.loginForm)
        })
        const data = await res.json()
        if (!res.ok) { this.authError = data.error; return }
        localStorage.setItem("token", data.access_token)
        localStorage.setItem("user",  JSON.stringify(data))
        this.currentUser = data
        this.loggedIn    = true
        if (data.role === "admin") this.loadDashboard()
      } catch(e) {
        this.authError = "Cannot connect to server. Is Flask running?"
      } finally {
        this.loading = false
      }
    },
    async exportApplications() {
      this.exportMessage = "Export started, please wait..."
      const res  = await fetch(`${API}/student/export`, {
        method:  "POST",
        headers: authHeaders()
      })
      const data = await res.json()
      if (!res.ok) { this.exportMessage = data.error; return }

      const taskId = data.task_id
      const checkStatus = async () => {
        const statusRes = await fetch(`${API}/student/export/status/${taskId}`, { headers: authHeaders() })
        const statusData = await statusRes.json()
        if (statusData.state === "SUCCESS") {
          this.exportMessage = `Export completed: ${statusData.result.filename}`
        } else {
          setTimeout(checkStatus, 1500)
        }
      }
      checkStatus()
    },
    async doRegister() {
      this.authError   = ""
      this.authSuccess = ""
      this.loading     = true
      try {
        const res  = await fetch(`${API}/auth/register`, {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify(this.registerForm)
        })
        const data = await res.json()
        if (!res.ok) { this.authError = data.error; return }
        this.authSuccess = data.message + " Please login."
        this.authTab     = "login"
      } catch(e) {
        this.authError = "Cannot connect to server. Is Flask running?"
      } finally {
        this.loading = false
      }
    },

    doLogout() {
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      this.loggedIn    = false
      this.currentUser = {}
      this.loginForm   = { username: "", password: "" }
    },

    async loadDashboard() {
      const res  = await fetch(`${API}/admin/dashboard`, { headers: authHeaders() })
      const data = await res.json()
      this.stats = data
    },

    async loadCompanies() {
      const res      = await fetch(`${API}/admin/companies?search=${this.companySearch}`, { headers: authHeaders() })
      this.companies = await res.json()
    },

    async loadStudents() {
      const res     = await fetch(`${API}/admin/students?search=${this.studentSearch}`, { headers: authHeaders() })
      this.students = await res.json()
    },

    async loadDrives() {
      const res   = await fetch(`${API}/admin/drives`, { headers: authHeaders() })
      this.drives = await res.json()
    },

    async loadApplications() {
      const res          = await fetch(`${API}/admin/applications`, { headers: authHeaders() })
      this.applications  = await res.json()
    },

    async updateCompanyStatus(id, status) {
      await fetch(`${API}/admin/companies/${id}/status`, {
        method:  "PUT",
        headers: authHeaders(),
        body:    JSON.stringify({ status })
      })
      this.loadCompanies()
    },
    async loadStudentDashboard() {
      const res          = await fetch(`${API}/student/dashboard`, { headers: authHeaders() })
      const data         = await res.json()
      this.studentStats  = data
      if (data.student) {
        this.editStudentForm = {
          full_name:   data.student.full_name   || "",
          roll_number: data.student.roll_number || "",
          branch:      data.student.branch      || "",
          department:  data.student.department  || "",
          cgpa:        data.student.cgpa        || "",
          year:        data.student.year        || "",
          phone:       data.student.phone       || "",
          skills:      data.student.skills      || ""
        }
      }
    },

    async loadStudentDrives() {
      const res           = await fetch(`${API}/student/drives?search=${this.driveSearch}`, { headers: authHeaders() })
      this.studentDrives  = await res.json()
    },

    async loadStudentApplications() {
      const res                = await fetch(`${API}/student/applications`, { headers: authHeaders() })
      this.studentApplications = await res.json()
    },

    async applyToDrive(driveId) {
      const res  = await fetch(`${API}/student/drives/${driveId}/apply`, {
        method:  "POST",
        headers: authHeaders()
      })
      const data = await res.json()
      if (!res.ok) { alert(data.error); return }
      alert(data.message)
      this.loadStudentDrives()
    },
    selectResume(event) {
    this.selectedResume = event.target.files[0];
  
    },

async uploadResume() {

    if (!this.selectedResume) {
        alert("Please select a PDF.");
        return;
    }

    const token = localStorage.getItem("token");

    const formData = new FormData();
    formData.append("resume", this.selectedResume);

    const res = await fetch(`${API}/student/resume`, {
        method: "POST",
        headers: {
            Authorization: "Bearer " + token
        },
        body: formData
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.error);
        return;
    }

    alert(data.message);

    this.loadStudentDashboard();
},

async viewResume() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch(`${API}/student/resume`, {
            headers: {
                Authorization: "Bearer " + token
            }
        });

        if (!response.ok) {
            const data = await response.json();
            alert(data.error);
            return;
        }

        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);

        window.open(url, "_blank");

    } catch (err) {
        alert("Unable to open resume.");
    }
},
    async saveStudentProfile() {
      const res  = await fetch(`${API}/student/profile`, {
        method:  "PUT",
        headers: authHeaders(),
        body:    JSON.stringify(this.editStudentForm)
      })
      const data = await res.json()
      if (!res.ok) { alert(data.error); return }
      this.showEditStudentProfile = false
      this.loadStudentDashboard()
    },

    async updateStudentStatus(id, action) {
      await fetch(`${API}/admin/students/${id}/status`, {
        method:  "PUT",
        headers: authHeaders(),
        body:    JSON.stringify({ action })
      })
      this.loadStudents()
    },

    async updateDriveStatus(id, status) {
      await fetch(`${API}/admin/drives/${id}/status`, {
        method:  "PUT",
        headers: authHeaders(),
        body:    JSON.stringify({ status })
      })
      this.loadDrives()
    },
    async loadCompanyDashboard() {
      const res         = await fetch(`${API}/company/dashboard`, { headers: authHeaders() })
      const data        = await res.json()
      this.companyStats = data
      if (data.company) {
        this.editProfileForm = {
          company_name:     data.company.company_name     || "",
          industry:         data.company.industry         || "",
          location:         data.company.location         || "",
          website:          data.company.website          || "",
          hr_contact_name:  data.company.hr_contact_name  || "",
          hr_contact_email: data.company.hr_contact_email || "",
          description:      data.company.description      || ""
        }
      }
    },

    async loadCompanyDrives() {
      const res          = await fetch(`${API}/company/drives`, { headers: authHeaders() })
      this.companyDrives = await res.json()
    },

    async createDrive() {
      this.driveError = ""
      const res  = await fetch(`${API}/company/drives`, {
        method:  "POST",
        headers: authHeaders(),
        body:    JSON.stringify(this.driveForm)
      })
      const data = await res.json()
      if (!res.ok) { this.driveError = data.error; return }
      this.showCreateDrive = false
      this.driveForm = {
        drive_name: "", job_title: "", job_description: "",
        eligibility_branch: "", eligibility_cgpa: "", eligibility_year: "",
        salary: "", location: "", application_deadline: "", interview_type: "In-person"
      }
      this.loadCompanyDrives()
    },

    async viewDriveApplications(drive) {
      this.selectedDrive = drive
      this.companyTab    = "applications"
      const res              = await fetch(`${API}/company/drives/${drive.id}/applications`, { headers: authHeaders() })
      this.driveApplications = await res.json()
    },

    async updateAppStatus(appId, status) {
      if (!status) return
      await fetch(`${API}/company/applications/${appId}/status`, {
        method:  "PUT",
        headers: authHeaders(),
        body:    JSON.stringify({ status })
      })
      this.viewDriveApplications(this.selectedDrive)
    },
    async loadPlacementHistory() {
      const res             = await fetch(`${API}/student/history`, { headers: authHeaders() })
      this.placementHistory = await res.json()
    },
    async saveProfile() {
      const res = await fetch(`${API}/company/profile`, {
        method:  "PUT",
        headers: authHeaders(),
        body:    JSON.stringify(this.editProfileForm)
      })
      const data = await res.json()
      if (!res.ok) { alert(data.error); return }
      this.showEditProfile = false
      this.loadCompanyDashboard()
    }
  }
}).mount("#app")
