# 📸 Step-by-Step: Deploy AutoMerch via Google Cloud Console

## Step 1: Build the Container Image

1. **Go to:** https://console.cloud.google.com/cloud-build/builds?project=automerch-app
2. **Click** the **"Create Build"** button (or the **"+"** button)
3. **Choose:** "Cloud Source Repositories" or scroll down and click **"Upload Archive"**
   
   **If using Upload Archive:**
   - Click **"Choose File"** or **"Browse"**
   - Create a ZIP file of your `automerch_remote` folder:
     - In PowerShell: `Compress-Archive -Path .\* -DestinationPath automerch.zip`
     - Upload `automerch.zip`
   
4. **Build configuration:** Select **"Cloud Build configuration file (yaml or json)"**
   - **Cloud Build configuration file location:** `cloudbuild.yaml`
   
   **OR** use **"Inline"** and paste:
   ```yaml
   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/automerch-app/automerch:latest', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'gcr.io/automerch-app/automerch:latest']
   images:
   - 'gcr.io/automerch-app/automerch:latest'
   ```

5. **Click** "Create" and wait for build to complete (5-10 minutes)

---

## Step 2: Deploy to Cloud Run

1. **Go to:** https://console.cloud.google.com/run?project=automerch-app
2. **Click** the **"Create Service"** button
3. **Select:** "Deploy one revision from an existing container image"
4. **Container image URL:** Click **"Select"** → Choose `gcr.io/automerch-app/automerch:latest`

---

## Step 3: Configure Basic Settings

1. **Service name:** `automerch`
2. **Region:** Select `us-central1` (or your preferred region)
3. **Deployment platform:** `Cloud Run (fully managed)`
4. **Authentication:** 
   - Select **"Allow unauthenticated invocations"** (so anyone with the URL can access it)

---

## Step 4: Configure Container (Step 9 - Environment Variables)

**Scroll down** to find the **"Container, Variables, Secrets, Connections"** section:

### 4.1 Container Tab
- **Container port:** `8000` (should auto-detect)
- **Memory:** Select `512 MiB`
- **CPU allocation:** Select `CPU is only allocated during request processing`
- **CPU:** Select `1`
- **Maximum requests per container:** `80` (default)
- **Request timeout:** `300` seconds
- **Maximum instances:** `10`

### 4.2 Variables & Secrets Tab (THIS IS STEP 9!)

**IMPORTANT:** You can deploy with minimal variables first to get the URL, then add Printful credentials later!

**Option A: Minimal Deployment (Get URL First)**
1. **Click on the "Variables & Secrets" tab** (it's right next to "Container" tab)
2. **Click the "Add Variable" button**
3. **Add only these minimal variables for now:**

   Click "Add Variable" → Fill in → Click "Add Variable" again for next one:
   
   | Variable Name | Variable Value |
   |--------------|----------------|
   | `AUTOMERCH_DRY_RUN` | `true` |
   | `ETSY_REDIRECT_URI` | `https://placeholder.run.app/auth/etsy/callback` |

   **Note:** We'll add Etsy and Printful credentials after we get the URL!

**Option B: Full Deployment (If you already have Etsy credentials)**
1. **Click on the "Variables & Secrets" tab**
2. **Click the "Add Variable" button**
3. **Add each environment variable one by one:**

   | Variable Name | Variable Value |
   |--------------|----------------|
   | `ETSY_CLIENT_ID` | `your_actual_client_id_here` |
   | `ETSY_CLIENT_SECRET` | `your_actual_secret_here` |
   | `ETSY_SHOP_ID` | `your_actual_shop_id_here` |
   | `ETSY_REDIRECT_URI` | `https://placeholder.run.app/auth/etsy/callback` |
   | `AUTOMERCH_DRY_RUN` | `true` (or `false` if you have Etsy set up) |

   **Note:** Skip `PRINTFUL_API_KEY` for now - we'll add it after registering with Printful!

4. **After adding all variables**, you should see them listed in the "Variables & Secrets" section

### 4.3 Connections Tab
- Leave default (no changes needed)

---

## Step 5: Deploy

1. **Scroll to the bottom** of the page
2. **Click the blue "Create" button**
3. **Wait for deployment** (about 2-3 minutes)
4. You'll see: **"Service automerch has been deployed"**

---

## Step 6: Get Your Service URL

After deployment completes, you'll see at the top of the page:

```
Service URL: https://automerch-abc123-uc.a.run.app
```

**Copy this URL!** You'll need it for the next step.

---

## Step 7: Update Etsy Redirect URI

1. **Go to:** https://www.etsy.com/developers/your-apps
2. **Click** on your app
3. **Find** "Redirect URI" field
4. **Update it to:** `https://YOUR_SERVICE_URL.run.app/auth/etsy/callback`
   - Replace `YOUR_SERVICE_URL` with the actual URL from Step 6
   - Example: `https://automerch-abc123-uc.a.run.app/auth/etsy/callback`
5. **Save** changes

---

## Step 8: Register with Printful

Now that you have your service URL, you can register with Printful:

1. **Copy your service URL** from Step 6 (e.g., `https://automerch-abc123-uc.a.run.app`)
2. **Go to:** https://www.printful.com/dashboard/api
3. **Register your app** with Printful
4. **Use your service URL** as the redirect/callback URL (if Printful asks for one)
5. **Get your Printful API key** from the dashboard

## Step 9: Update Cloud Run Environment Variables

Now add all your credentials:

1. **Go back to:** https://console.cloud.google.com/run?project=automerch-app
2. **Click** on your `automerch` service
3. **Click** "Edit & Deploy New Revision" (top right)
4. **Click** "Variables & Secrets" tab
5. **Update/add variables:**

   **If you haven't added Etsy credentials yet:**
   - Click "Add Variable" for each:
     - `ETSY_CLIENT_ID` = your Etsy client ID
     - `ETSY_CLIENT_SECRET` = your Etsy secret
     - `ETSY_SHOP_ID` = your Etsy shop ID
     - `PRINTFUL_API_KEY` = your Printful API key (from Step 8)
   
   **Update existing variables:**
   - Find `ETSY_REDIRECT_URI` → Click pencil icon → Update to: `https://YOUR_SERVICE_URL.run.app/auth/etsy/callback`
   - Find `AUTOMERCH_DRY_RUN` → Click pencil icon → Update to: `false` (if you want real API calls)

6. **Click** "Deploy" at the bottom
7. **Wait** for new revision to deploy

---

## Step 9: Test Your Deployment

1. **Visit:** `https://YOUR_SERVICE_URL.run.app`
2. **You should see** your AutoMerch dashboard
3. **Test OAuth:** Visit `https://YOUR_SERVICE_URL.run.app/auth/etsy/login`
4. **Test Research:** Visit `https://YOUR_SERVICE_URL.run.app/research`

---

## ✅ Done!

Your AutoMerch app is now live on Google Cloud with a permanent HTTPS URL! 🎉

**Your service URL:** `https://YOUR_SERVICE_URL.run.app`

