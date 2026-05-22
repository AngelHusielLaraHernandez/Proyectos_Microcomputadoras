'This Software is licensed by OCP Omni Consumer Prdoucts.
Imports System
Imports System.IO
Imports System.Data
Imports System.Text
Imports System.Windows.Forms

Public Class Form1
    Dim WithEvents serialPort1 As New IO.Ports.SerialPort
    Dim port1connected As Boolean = False
    Dim reqInstruction As Integer = 0 'keeps track of command number sent 
    Dim rxComplete As Boolean = False 'tracks if serial data recieved
    Dim Rxdata1 As String 'the serial data

    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        For i As Integer = 0 To My.Computer.Ports.SerialPortNames.Count - 1
            cbbCOMPorts1.Items.Add(My.Computer.Ports.SerialPortNames(i))
        Next
    End Sub


    Private Sub btnConnect1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnConnect1.Click
        '-------------------------------------------
        ' Event handler for the Connect button
        '-------------------------------------------
        If serialPort1.IsOpen Then
            serialPort1.Close()
        End If

        Try
            With serialPort1
                .PortName = cbbCOMPorts1.Text
                .BaudRate = 38400 '115200 '9600 '19200 '38400 for hc05 is default
                .Parity = IO.Ports.Parity.None
                .DataBits = 8
                .StopBits = IO.Ports.StopBits.One
                .Encoding = System.Text.Encoding.Default
                '.WriteBufferSize = 4096
                '.DtrEnable = True 'resests the arduin ?
                '.ReadBufferSize = 40
                '.ReceivedBytesThreshold = 1 'expected number of bytes to receive. usefull
                .ReadTimeout = 400
            End With
            serialPort1.Open()
            lblMessage1.Text = serialPort1.PortName & " Port Open"
            lblMessage1.BackColor = Color.OliveDrab
            btnConnect1.Enabled = False
            btnDisconnect1.Enabled = True
            port1connected = True

        Catch ex As Exception
            MsgBox("Select a Port or That port is being used/unavailable") '& ex.ToString)
        End Try

    End Sub

    Private Sub btnDisconnect1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDisconnect1.Click
        ' Event handler for the Disconnect button
        '-------------------------------------------
        Try
            serialPort1.Close()
            lblMessage1.Text = serialPort1.PortName & " Port Closed"
            lblMessage1.BackColor = Color.Firebrick
            btnConnect1.Enabled = True
            btnDisconnect1.Enabled = False
            port1connected = False
        Catch ex As Exception
            MsgBox(ex.ToString)
        End Try

    End Sub

    '-------------------------------------------
    ' Event handler for the DataReceived1
    '-------------------------------------------
    Private Sub DataReceived1(ByVal sender As Object, ByVal e As System.IO.Ports.SerialDataReceivedEventArgs) Handles serialPort1.DataReceived
       
        txtDataReceived1.Invoke(New myDelegate1(AddressOf updateTextBox1), New Object() {})
    End Sub
    Public Delegate Sub myDelegate1()
    ''this seems this messy but works

    Public Sub updateTextBox1()
        While serialPort1.BytesToWrite > 0 'infiniate loop until txbuffer is empty 
        End While

        Try
            Rxdata1 = serialPort1.ReadLine 'read until newline is detected
            serialPort1.DiscardInBuffer() ''clear rx buffer once lf read
            txtDataReceived1.AppendText(Rxdata1 & vbCrLf) 'updates the console text box

            If reqInstruction = 1 Then 'this is the instruction number the loop is current on
                TextBox1.Clear()
                TextBox1.AppendText(Rxdata1)
                If Not Rxdata1.Contains("OK") Then ''this is very basic error checking to make sure the programed received 'OK' from HC05
                    rxComplete = True
                End If
            End If

            If reqInstruction = 2 Then
                Rxdata1 = Rxdata1.Replace("+VERSION:", "")
                TextBox2.Clear()
                TextBox2.AppendText(Rxdata1)
            End If

            If reqInstruction = 3 Then
                Rxdata1 = Rxdata1.Replace("+UART:", "")
                TextBox3.Clear()
                TextBox3.AppendText(Rxdata1)
            End If

            If reqInstruction = 4 Then
                Rxdata1 = Rxdata1.Replace("+ROLE:", "")
                TextBox4.Clear()
                TextBox4.AppendText(Rxdata1)
            End If

            If reqInstruction = 5 Then
                Rxdata1 = Rxdata1.Replace("+NAME:", "")
                TextBox5.Clear()
                TextBox5.AppendText(Rxdata1)
            End If

            If reqInstruction = 6 Then
                Rxdata1 = Rxdata1.Replace("+PSWD:", "")
                TextBox6.Clear()
                TextBox6.AppendText(Rxdata1)
            End If

            If reqInstruction = 7 Then
                Rxdata1 = Rxdata1.Replace("+POLAR:", "")
                TextBox7.Clear()
                TextBox7.AppendText(Rxdata1)
            End If

            If reqInstruction = 8 Then
                Rxdata1 = Rxdata1.Replace("+ADDR:", "")
                TextBox8.Clear()
                TextBox8.AppendText(Rxdata1)
            End If


            reqInstruction = reqInstruction + 1
        Catch ex As TimeoutException
            MsgBox(" Read Error - Try again" + vbCr + ex.ToString)
        End Try

    End Sub


    Private Sub Button1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button1.Click
        If CheckBox1.Checked = False Then 'read mode stuff
            reqInstruction = 0
            If serialPort1.IsOpen Then
                If ComboBox1.SelectedValue = 0 Then ''tweak because command AT doesnt use a "?"
                    System.Threading.Thread.Sleep(100)
                    serialPort1.WriteLine(ComboBox1.Text & vbCr)
                Else
                    System.Threading.Thread.Sleep(100)
                    serialPort1.WriteLine(ComboBox1.Text & "?" & vbCr) 'all other read coammnds require ?
                End If
            End If
        Else 'write mode stuff
            reqInstruction = 0
            If serialPort1.IsOpen Then
                System.Threading.Thread.Sleep(100)
                serialPort1.WriteLine(ComboBox1.Text & "=" & txt_WriteCommands.Text & vbCr) 'this will not check what you send but should return error in the console
            End If

        End If



    End Sub

    Private Sub ClearAll()
        Rxdata1 = ""
        txtDataReceived1.Clear()
        txtDataReceived1.Update()
        TextBox1.Clear()
        TextBox1.Update()
        TextBox2.Clear()
        TextBox2.Update()
        TextBox3.Clear()
        TextBox3.Update()
        TextBox4.Clear()
        TextBox4.Update()
        TextBox5.Clear()
        TextBox5.Update()
        TextBox6.Clear()
        TextBox6.Update()
        TextBox7.Clear()
        TextBox7.Update()
        TextBox8.Clear()
        TextBox8.Update()
    End Sub



    Private Sub WaitForRx()
        While (serialPort1.BytesToRead <> 0 And rxComplete = False) ''infinite loop if receive buffer still has data AND rxComplete is false
            updateTextBox1()
        End While
    End Sub



    Private Sub Button2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button2.Click
        rxComplete = False
        reqInstruction = 1
        ClearAll()


        If serialPort1.IsOpen Then

            Label8.ForeColor = Color.White
            Label8.Text = "Working..."

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+VERSION?" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+UART?" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+ROLE?" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+NAME?" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+PSWD?" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+POLAR?" & vbCr)
            End If

            WaitForRx()

            If serialPort1.IsOpen And rxComplete = False Then
                System.Threading.Thread.Sleep(400)
                serialPort1.WriteLine("AT+ADDR?" & vbCr)
            End If



            Label8.ForeColor = Color.Green ''each command was sent
            Label8.Text = "Read Complete"

            If Not TextBox1.Text.Contains("OK") Then 'clears the text if a failed read
                'ReadFailed()
                Label8.ForeColor = Color.Red
                Label8.Text = "NOT OK. Try Again"
                ClearAll()
            End If

        End If
    End Sub




    Private Sub Button4_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button4.Click
        If serialPort1.IsOpen Then
            serialPort1.WriteLine("AT+ORGL")
        End If
    End Sub




    Private Sub CheckBox1_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CheckBox1.CheckedChanged
        If CheckBox1.Checked = False Then
            Button1.ForeColor = Color.White
            Button1.Text = "Send READ Command"
            CheckBox1.Text = "Read Only"
            CheckBox1.BackColor = Color.DarkGreen
            Label9.Text = "?"
            txt_WriteCommands.Enabled = False
        Else
            Button1.ForeColor = Color.Red
            Button1.Text = "Send WRITE Command"
            CheckBox1.Text = "WRITE ENABLED"
            CheckBox1.BackColor = Color.Firebrick
            Label9.Text = "="
            txt_WriteCommands.Enabled = True
        End If
    End Sub


    Private Sub Button5_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button5.Click
        Me.Close()

    End Sub

    Private Sub Button6_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button6.Click
        Form2.Show()
    End Sub


    Private Sub Button3_Click_1(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Button3.Click
        ClearAll()
    End Sub
End Class
