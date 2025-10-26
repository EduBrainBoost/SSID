
package ssid.security.autorollback

default rollback = false

rollback {
  input.score < 70
}
