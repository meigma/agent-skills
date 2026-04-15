# Deployment

Docusaurus generates static files that can be deployed to any static hosting provider. The build output is a fully static site that works without server-side rendering.

## Building for Production

```bash
# Build the site
npm run build

# Output is in /build directory
ls build/
```

The build command:
1. Bundles all React code
2. Pre-renders all pages to static HTML
3. Copies static assets
4. Generates sitemap and other metadata

### Test Production Build Locally

```bash
npm run serve
```

This serves the `/build` directory locally on port 3000.

## Environment Variables

Set build-time environment variables:

```bash
# Build with custom base URL
BASE_URL=/docs/ npm run build

# Build with environment-specific config
NODE_ENV=production npm run build
```

Access in config:

```typescript
const config: Config = {
  baseUrl: process.env.BASE_URL || '/',
};
```

## GitHub Pages

### Using GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Configuration for GitHub Pages

```typescript
// docusaurus.config.ts
const config: Config = {
  // For https://username.github.io/
  url: 'https://username.github.io',
  baseUrl: '/',

  // For https://username.github.io/repo-name/
  url: 'https://username.github.io',
  baseUrl: '/repo-name/',

  // For custom domain
  url: 'https://docs.example.com',
  baseUrl: '/',

  organizationName: 'username',  // GitHub username or org
  projectName: 'repo-name',      // Repository name
  trailingSlash: false,
};
```

### Custom Domain

Create `static/CNAME`:

```
docs.example.com
```

## Vercel

### Zero-Config Deployment

1. Connect your repository to Vercel
2. Vercel auto-detects Docusaurus
3. Deploys automatically on push

### vercel.json (Optional)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "docusaurus-2",
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        }
      ]
    }
  ]
}
```

### Environment Variables in Vercel

Set in Vercel Dashboard > Settings > Environment Variables:

```
ALGOLIA_APP_ID=xxx
ALGOLIA_API_KEY=xxx
```

## Netlify

### netlify.toml

```toml
[build]
  command = "npm run build"
  publish = "build"

[build.environment]
  NODE_VERSION = "20"

# Redirect rules
[[redirects]]
  from = "/old-path/*"
  to = "/new-path/:splat"
  status = 301

# Headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"

# SPA fallback
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Netlify Build Plugin for Cache

```toml
[[plugins]]
  package = "netlify-plugin-cache"
  [plugins.inputs]
    paths = [
      "node_modules/.cache",
      ".docusaurus"
    ]
```

## Cloudflare Pages

### Configuration

1. Connect repository in Cloudflare Dashboard
2. Set build command: `npm run build`
3. Set output directory: `build`
4. Set Node.js version: `20`

### _headers File

Create `static/_headers`:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

/assets/*
  Cache-Control: public, max-age=31536000, immutable
```

### _redirects File

Create `static/_redirects`:

```
/old-page  /new-page  301
/docs/old/*  /docs/new/:splat  301
```

## Docker

### Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # SPA fallback
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Cache static assets
        location /assets/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Security headers
        add_header X-Frame-Options "DENY";
        add_header X-Content-Type-Options "nosniff";

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    }
}
```

### Docker Compose

```yaml
version: '3.8'
services:
  docs:
    build: .
    ports:
      - "3000:80"
    restart: unless-stopped
```

## AWS S3 + CloudFront

### S3 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### Deploy Script

```bash
#!/bin/bash
npm run build
aws s3 sync build/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### GitHub Actions for S3

```yaml
- name: Deploy to S3
  uses: jakejarvis/s3-sync-action@master
  with:
    args: --delete
  env:
    AWS_S3_BUCKET: ${{ secrets.AWS_S3_BUCKET }}
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    SOURCE_DIR: 'build'

- name: Invalidate CloudFront
  uses: chetan/invalidate-cloudfront-action@v2
  env:
    DISTRIBUTION: ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}
    PATHS: '/*'
    AWS_REGION: 'us-east-1'
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Build Optimizations

### Faster Builds with Rspack

```bash
npm install @docusaurus/faster
```

```typescript
// docusaurus.config.ts
const config: Config = {
  future: {
    experimental_faster: true,
  },
};
```

### Reduce Bundle Size

```typescript
// docusaurus.config.ts
const config: Config = {
  // Remove unused locales
  i18n: {
    locales: ['en'],  // Only build needed locales
  },

  // Disable unused features
  presets: [
    ['classic', {
      blog: false,  // Disable blog if not used
      docs: {
        // Only include necessary versions
        onlyIncludeVersions: ['current'],
      },
    }],
  ],
};
```

### Analyze Bundle

```bash
npm run build -- --bundle-analyzer
```

## CI/CD Best Practices

1. **Cache dependencies** - Cache `node_modules` and `.docusaurus`
2. **Run checks first** - Lint and test before building
3. **Preview deployments** - Deploy PRs to preview URLs
4. **Broken link checking** - Set `onBrokenLinks: 'throw'`
5. **Build matrix** - Test on multiple Node versions if needed

### Complete GitHub Actions Example

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build
        env:
          NODE_OPTIONS: --max-old-space-size=4096

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci
      - run: npm run build

      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```
