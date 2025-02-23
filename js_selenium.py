def js_sends_key(driver, e, content):
    driver.execute_async_script("""
    var e = arguments[0];
    var strings = arguments[1];
    var callback = arguments[2]; // Selenium's built-in async callback

    var index = 0;

    function typeCharacter() {
        if (index >= strings.length) {
            callback(); // ✅ Notify Selenium that execution is complete
            return;
        }

        var char = strings[index++];
        e.focus(); // Ensure the element is focused
        if (char === "\\n") { // Handle Enter key
            ["keydown", "keypress", "keyup"].forEach(function(eventType) {
                var event = new KeyboardEvent(eventType, {
                    key: "Enter",
                    code: "Enter",
                    keyCode: 13,
                    bubbles: true
                });
                e.dispatchEvent(event);
            });
        } else {
            document.execCommand("insertText", false, char);
            e.dispatchEvent(new Event("input", { bubbles: true }));
            e.dispatchEvent(new Event("change", { bubbles: true }));
        }

        // Simulate typing delay
        setTimeout(typeCharacter, Math.random() * 100 + 50);
    }

    typeCharacter(); // Start typing process
    """, e, content)


def js_type_input(driver, e, value):
    driver.execute_async_script("""
        var e = arguments[0];
        var strings = arguments[1];
        var callback = arguments[2]; // Selenium's built-in async callback
        e.setAttribute("type","hidden");
        e.setAttribute("value", strings);
        callback();
    """, e, value)