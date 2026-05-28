window.addEventListener('load', () => {
    const send = async (payload) => {
      console.log('SEND ->', payload)
      document.getElementById('lastSent').innerText = 'Last: ' + JSON.stringify(payload)
      try {
        const res = await fetch('/control', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error(res.statusText)
        await res.json()
        document.getElementById('backendStatus').innerText = 'OK'
      } catch (err) {
        document.getElementById('backendStatus').innerText = 'Error'
        console.error(err)
      }
    }
  
    function attachHold(button, payload) {
      let interval = null
      const start = () => {
        send(payload)
        interval = setInterval(() => send(payload), 200)
      }
      const stop = () => {
        if (interval) {
          clearInterval(interval)
          interval = null
        }
      }
      button.addEventListener('mousedown', start)
      button.addEventListener('touchstart', start)
      button.addEventListener('mouseup', stop)
      button.addEventListener('mouseleave', stop)
      button.addEventListener('touchend', stop)
      button.addEventListener('touchcancel', stop)
    }
  
    document.querySelectorAll('#wheelJoystick .joy-btn').forEach(btn => {
      const action = btn.dataset.action
      attachHold(btn, { component: 'wheels', action: action, ts: Date.now() })
    })
  
    document.querySelectorAll('#armJoystick .joy-btn').forEach(btn => {
      const action = btn.dataset.action
      attachHold(btn, { component: 'arm', action: action, ts: Date.now() })
    })
  
    document.getElementById('shoulderLeft').addEventListener('click', () => send({ component: 'arm', action: 'shoulder_left', ts: Date.now() }))
    document.getElementById('shoulderRight').addEventListener('click', () => send({ component: 'arm', action: 'shoulder_right', ts: Date.now() }))
  
    const gripperBtn = document.getElementById('gripper')
    let gripperOpen = false
    gripperBtn.addEventListener('click', () => {
      gripperOpen = !gripperOpen
      gripperBtn.innerText = gripperOpen ? 'Open' : 'Close'
      send({ component: 'gripper', action: gripperOpen ? 'open' : 'close', ts: Date.now() })
    })
  
    document.querySelectorAll('#modeSwitch button').forEach(b => {
      b.addEventListener('click', () => {
        document.querySelectorAll('#modeSwitch button').forEach(x => x.classList.remove('active'))
        b.classList.add('active')
        send({ component: 'system', action: 'mode', mode: b.dataset.mode, ts: Date.now() })
      })
    })
  
    const video = document.getElementById('fpvVideo')
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true, audio: false }).then(s => {
        video.srcObject = s
      }).catch(e => console.error('Camera error:', e))
    }
  
    const frame = document.getElementById('videoFrame')
    const maxBtn = document.getElementById('maximizeBtn')
    maxBtn.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        frame.requestFullscreen().catch(err => console.warn(err))
      } else {
        document.exitFullscreen()
      }
    })
  });
