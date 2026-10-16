// DeskTrace's own non-sensitive WinForms fixture, MIT licensed.
using System;
using System.Drawing;
using System.Windows.Forms;

class Fixture : Form {
    [STAThread]
    static void Main(string[] args) {
        Application.EnableVisualStyles();
        Application.Run(new Fixture(args));
    }
    Fixture(string[] args) {
        Text = "DeskTrace owned regression fixture";
        ClientSize = new Size(620, 300);
        StartPosition = FormStartPosition.Manual;
        Location = new Point(40, 40);
        var label = new Label { Text = "Public test input", Location = new Point(20, 20), Width = 560 };
        var input = new TextBox { Name = "input", AccessibleName = "Public input", Location = new Point(20, 50), Width = 560 };
        var apply = new Button { Name = "apply", AccessibleName = "Apply", Text = "Apply", Location = new Point(20, 95), Width = 140 };
        var output = new TextBox { Name = "output", AccessibleName = "Public output", ReadOnly = true, Location = new Point(20, 145), Width = 560 };
        apply.Click += delegate { output.Text = input.Text; };
        Controls.AddRange(new Control[] { label, input, apply, output });
        if (Array.IndexOf(args, "--password-control") >= 0) {
            Controls.Add(new TextBox { Name = "password", UseSystemPasswordChar = true, Location = new Point(20, 200), Width = 300 });
        }
        if (Array.IndexOf(args, "--duplicate-control") >= 0) {
            Controls.Add(new TextBox { Name = "input", Location = new Point(20, 240), Width = 300 });
        }
    }
}
