$(function() {

    /**
     * Select all checkboxes of the class row-selector
     */
    $("#select-all").click(function(event) {
        event.preventDefault();
        $(".row-selector").prop('checked', true);
    });

    /**
     * Remove the selection from all row-selector checkboxes.
     */
    $("#select-none").click(function(event) {
        event.preventDefault();
        $(".row-selector").prop('checked', false);
    });

    /**
     * Invert the selection state for all row-selector checkboxes.
     */
    $("#invert-selection").click(function(event) {
        event.preventDefault();

        $(".row-selector").each(function(index) {
            $(this).prop('checked', !$(this).prop('checked'));
        });
    });

    /**
     * Submit the json-editor form.
     */
    $("#save-document").click(function(event) {
        event.preventDefault();
        $("#doc-data-field").attr("value", window.jsoneditor.getText());
        $("#update-document-form").submit();
    });

    /**
     * Open the deletion confirmation dialog to delete documents.
     * Checks if any are selected at all and writes the size of the
     * selection into the dialog.
     */
    $("#delete-selected-docs").click(function(event) {
        event.preventDefault();
        var selection_size = $(".row-selector:checked").length;
        if (selection_size > 0) {
            $("#selection-size").text(selection_size);
            $("#confirm-delete").modal();
        }
    });

    $("#confirm-delete-ok").click(function(event) {
        event.preventDefault();
        $("#delete-docs-form").submit();
    });

    $("#confirm-delete-collection-ok").click(function(event) {
        event.preventDefault();

        $("#delete-collection-form").submit();
    });

    $("#create-col-form-submit").click(function(event) {
        event.preventDefault();
        if ($("#col-name").attr("value").length > 1) {
            $("#create-col-form").submit();
        }
    });

    $(".delete-collection").click(function(event) {
        event.preventDefault();
        var col_name = $(this).attr("col");
        $("#collection-name").text(col_name);
        $("#col-name-input").attr("value", col_name);
        $("#confirm-delete").modal();
    });

    $(".delete-database").click(function(event) {
        event.preventDefault();
        var db_name = $(this).attr("db");
        $("#db-name").text(db_name);
        $("#db-name-input").attr("value", db_name);
        $("#confirm-delete").modal();
    });

    // Configure extended and simple json editor for filtering
    function send_if_valid() {
        // This flag prevents change events while the editor is being set up
        if (!window.editor_loaded) {
            return;
        }
        // Catch exceptions or else the cursor will not move behind the typed char.
        try {
            send_query(JSON.stringify(window.jsoneditor.get()));
        } catch(err) {

        }
    }
    
    // Auto parse json input on text change
    $("#query").bind("input", function() {
        var data = null;
        var value = $("#query").val();
        if (!value) {
            value = "{}";
        }
        try {
            eval("data = " + value);
        } catch(err) {
            return;
        }
        send_query(JSON.stringify(data));
    });

    window.editor_loaded = false;
    var container = document.getElementById("extended-editor-editor");
    var options = {
            mode: 'code',
            search: false,
            modes: ['code', 'tree'],
            change: send_if_valid,
        };
    window.jsoneditor = new jsoneditor.JSONEditor(container, options);
    window.editor_loaded = true;

    $('#extend-editor').bind('click', function() {
        $('#simple-editor').hide(0);

        // Copy json data from simple input to extended editor
        var data = null;
        var value = $("#query").val();
        if (!value) {
            value = "{}";
        }
        try {
            eval("data = " + value);
            window.jsoneditor.set(data);
        } catch(err) {
        }
        $('#extended-editor').slideDown(400, function() {
            // TODO: Focus on the editor so the user can start typing immediately
            //$('#extended-editor-editor .ace_editor .ace_scroller')[0].focus();
        });
    });

    $('#collapse-editor').bind('click', function() {
        $('#extended-editor').slideUp(400, function() {
            // Copy stringified json to simple editor
            $('#simple-editor input').val(JSON.stringify(window.jsoneditor.get()));
            $('#simple-editor').show(0);
            $('#simple-editor input')[0].focus();
        });
    });
})

// Send current query to datatable and call a refresh
window.current_query = null;
function send_query(json) {
    window.current_query = json
    $('#doc-table').dataTable().fnReloadAjax();
    
}

function table_rendered() {
    // Nothing to do
}

