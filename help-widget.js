(function(){
  var css = `
  #qnsHelpBtn{position:fixed;bottom:24px;right:24px;width:56px;height:56px;border-radius:50%;background:var(--accent,#c9a54e);border:none;cursor:pointer;z-index:500;box-shadow:0 8px 24px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center;transition:transform .2s}
  #qnsHelpBtn:hover{transform:scale(1.06)}
  #qnsHelpBtn svg{width:26px;height:26px;stroke:#0a0a0a}
  #qnsHelpPanel{position:fixed;bottom:92px;right:24px;width:320px;max-width:calc(100vw - 40px);background:#fff;border-radius:14px;box-shadow:0 16px 48px rgba(0,0,0,.28);z-index:500;display:none;overflow:hidden;font-family:var(--sans),'DM Sans',sans-serif}
  #qnsHelpPanel.open{display:block}
  #qnsHelpPanel .qns-help-head{background:#0a0a0a;color:#fff;padding:18px 20px;font-family:var(--serif),'DM Serif Display',serif;font-size:18px}
  #qnsHelpPanel .qns-help-head span{display:block;font-family:var(--sans),'DM Sans',sans-serif;font-size:12px;color:rgba(255,255,255,.5);margin-top:4px;font-weight:400}
  #qnsHelpPanel .qns-help-body{padding:18px 20px}
  #qnsHelpPanel textarea{width:100%;min-height:100px;border:1px solid #ddd;border-radius:8px;padding:10px;font-family:var(--sans),'DM Sans',sans-serif;font-size:14px;resize:vertical;box-sizing:border-box}
  #qnsHelpPanel button.qns-send{margin-top:12px;width:100%;background:var(--accent,#c9a54e);color:#0a0a0a;border:none;padding:12px;border-radius:8px;font-weight:700;cursor:pointer;font-size:14px}
  #qnsHelpPanel button.qns-send:hover{background:var(--accent-hover,#dbbe6e)}
  #qnsHelpPanel .qns-help-alt{margin-top:10px;font-size:12px;color:#888;text-align:center}
  #qnsHelpPanel .qns-help-alt a{color:var(--accent,#c9a54e)}
  #qnsHelpClose{position:absolute;top:14px;right:16px;background:none;border:none;color:rgba(255,255,255,.6);font-size:18px;cursor:pointer;line-height:1}
  `;
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var btn = document.createElement('button');
  btn.id = 'qnsHelpBtn';
  btn.setAttribute('aria-label', 'Ask a question');
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';

  var panel = document.createElement('div');
  panel.id = 'qnsHelpPanel';
  panel.innerHTML = '<div class="qns-help-head" style="position:relative">Have a question?<span>Send it directly, no forms to hunt for.</span><button id="qnsHelpClose" aria-label="Close">&times;</button></div><div class="qns-help-body"><textarea id="qnsHelpMsg" placeholder="What do you want to know?"></textarea><button class="qns-send" id="qnsHelpSend">Send via Email</button><div class="qns-help-alt">Or email directly: <a href="mailto:Brett@quantumneuroshift.com">Brett@quantumneuroshift.com</a></div></div>';

  document.addEventListener('DOMContentLoaded', function(){
    document.body.appendChild(btn);
    document.body.appendChild(panel);

    btn.addEventListener('click', function(){
      panel.classList.toggle('open');
    });
    document.getElementById('qnsHelpClose').addEventListener('click', function(){
      panel.classList.remove('open');
    });
    document.getElementById('qnsHelpSend').addEventListener('click', function(){
      var msg = document.getElementById('qnsHelpMsg').value.trim();
      if(!msg){ return; }
      var subject = encodeURIComponent('Question from quantumneuroshift.com');
      var body = encodeURIComponent(msg);
      window.location.href = 'mailto:Brett@quantumneuroshift.com?subject=' + subject + '&body=' + body;
    });
  });
})();
