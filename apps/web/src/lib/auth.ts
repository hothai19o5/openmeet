import NextAuth, { type NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import KeycloakProvider from 'next-auth/providers/keycloak'

declare module 'next-auth' {
  interface Session {
    accessToken?: string
    user: {
      id: string
      name?: string | null
      email?: string | null
      role?: 'admin' | 'member' | 'guest'
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id?: string
    role?: string
    accessToken?: string
  }
}

/** Map Keycloak realm_roles array → single app role */
function mapKeycloakRole(realmRoles?: string[]): 'admin' | 'member' | 'guest' {
  if (!realmRoles) return 'member'
  if (realmRoles.includes('admin')) return 'admin'
  if (realmRoles.includes('member')) return 'member'
  if (realmRoles.includes('guest')) return 'guest'
  return 'member'
}

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET ?? 'dev-secret-change-in-production',
  session: { strategy: 'jwt', maxAge: 60 * 60 * 8 },
  pages: { signIn: '/login', error: '/login' },
  providers: [
    // ── Credentials (dev / fallback) ──
    CredentialsProvider({
      id: 'credentials',
      name: 'Username & Password',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const { username, password } = credentials ?? {}
        if (!username || !password || password.length < 4) return null

        // If Keycloak is configured, validate via ROPC grant
        if (process.env.KEYCLOAK_URL && process.env.KEYCLOAK_CLIENT_ID) {
          try {
            const tokenUrl = `${process.env.KEYCLOAK_URL}/realms/${process.env.KEYCLOAK_REALM}/protocol/openid-connect/token`
            const res = await fetch(tokenUrl, {
              method: 'POST',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: new URLSearchParams({
                grant_type: 'password',
                client_id: process.env.KEYCLOAK_CLIENT_ID,
                client_secret: process.env.KEYCLOAK_CLIENT_SECRET ?? '',
                username,
                password,
              }),
            })

            if (!res.ok) return null

            const data = await res.json()
            // Decode access_token to get roles
            const payload = JSON.parse(
              Buffer.from(data.access_token.split('.')[1], 'base64').toString()
            )

            return {
              id: payload.sub,
              name: payload.name ?? username,
              email: payload.email ?? `${username}@openmeet.local`,
              role: mapKeycloakRole(payload.realm_roles),
              accessToken: data.access_token,
            }
          } catch (err) {
            console.error('[auth] Keycloak ROPC failed:', err)
            return null
          }
        }

        // Fallback: stub auth (no Keycloak)
        return {
          id: username,
          name: username.charAt(0).toUpperCase() + username.slice(1),
          email: `${username}@openmeet.local`,
          role: username === 'admin' ? 'admin' : 'member',
        }
      },
    }),

    // ── Keycloak OIDC (SSO button) ──
    ...(process.env.KEYCLOAK_CLIENT_ID
      ? [
          KeycloakProvider({
            clientId: process.env.KEYCLOAK_CLIENT_ID,
            clientSecret: process.env.KEYCLOAK_CLIENT_SECRET ?? '',
            issuer: `${process.env.KEYCLOAK_URL}/realms/${process.env.KEYCLOAK_REALM}`,
          }),
        ]
      : []),
  ],

  callbacks: {
    async jwt({ token, user, account, profile }) {
      // First login — persist user info into JWT
      if (user) {
        token.id = (user as any).id ?? user.id
        token.role = (user as any).role ?? 'member'
      }
      // Keycloak OIDC flow — extract roles from profile
      if (account?.provider === 'keycloak' && profile) {
        const kc = profile as any
        token.role = mapKeycloakRole(kc.realm_roles)
      }
      if (account?.access_token) token.accessToken = account.access_token
      // From credentials ROPC
      if ((user as any)?.accessToken) token.accessToken = (user as any).accessToken
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken
      session.user = {
        ...session.user,
        id: (token.id ?? token.sub) as string,
        role: (token.role ?? 'member') as 'admin' | 'member' | 'guest',
      }
      return session
    },
  },
}

// Default export for /api/auth/[...nextauth] route handler
const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
