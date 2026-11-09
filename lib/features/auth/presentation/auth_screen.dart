import 'package:flutter/material.dart';

import '../../../main_shell.dart';

/// Kirish / Ro'yxatdan o'tish sahifasi.
/// Logindan keyin HomeScreen ochiladi.
class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

enum _Mode { login, register }

class _AuthScreenState extends State<AuthScreen> {
  _Mode _mode = _Mode.login;
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscure = true;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _submit() {
    final email = _email.text.trim();
    final password = _password.text;

    if (email.isEmpty || password.isEmpty) {
      _toast('Email va parolni kiriting');
      return;
    }
    if (_mode == _Mode.register &&
        (password.length < 6 || _name.text.trim().length < 2)) {
      _toast('Ma’lumotlarni to‘liq kiriting (parol 6+ belgi)');
      return;
    }

    // Muvaffaqiyatli kirish → home page
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => const MainShell()),
    );
  }

  void _toast(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRegister = _mode == _Mode.register;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ---------------- Logotip ----------------
                Center(
                  child: Container(
                    width: 68,
                    height: 68,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Center(
                      child: Text('S.',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 30,
                              fontWeight: FontWeight.w800)),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Text('SprichDe',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineSmall
                        ?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 6),
                Text(
                  isRegister
                      ? 'Hisob yarating va o‘rganishni boshlang'
                      : 'Nemischa o‘rganishni davom ettiring',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyMedium?.copyWith(
                      color:
                          theme.colorScheme.onSurface.withValues(alpha: 0.55)),
                ),
                const SizedBox(height: 28),

                // ---------------- Maydonlar ----------------
                if (isRegister) ...[
                  _Field(
                    controller: _name,
                    label: 'Ism va familiya',
                    icon: Icons.person_outline_rounded,
                  ),
                  const SizedBox(height: 12),
                ],
                _Field(
                  controller: _email,
                  label: 'Email',
                  icon: Icons.mail_outline_rounded,
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 12),
                _Field(
                  controller: _password,
                  label: 'Parol',
                  icon: Icons.lock_outline_rounded,
                  obscure: _obscure,
                  suffix: IconButton(
                    icon: Icon(
                        _obscure
                            ? Icons.visibility_off_outlined
                            : Icons.visibility_outlined,
                        size: 20),
                    onPressed: () => setState(() => _obscure = !_obscure),
                  ),
                ),
                const SizedBox(height: 22),

                // ---------------- Asosiy tugma ----------------
                SizedBox(
                  height: 52,
                  child: FilledButton(
                    onPressed: _submit,
                    style: FilledButton.styleFrom(
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15)),
                    ),
                    child: Text(
                      isRegister ? 'Ro‘yxatdan o‘tish' : 'Kirish',
                      style: const TextStyle(
                          fontSize: 15, fontWeight: FontWeight.w700),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // ---------------- Rejim almashtirish ----------------
                TextButton(
                  onPressed: () => setState(() => _mode =
                      isRegister ? _Mode.login : _Mode.register),
                  child: Text(
                    isRegister
                        ? 'Hisobingiz bormi? Kirish'
                        : 'Hisobingiz yo‘qmi? Ro‘yxatdan o‘tish',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Field extends StatelessWidget {
  const _Field({
    required this.controller,
    required this.label,
    required this.icon,
    this.obscure = false,
    this.keyboardType,
    this.suffix,
  });

  final TextEditingController controller;
  final String label;
  final IconData icon;
  final bool obscure;
  final TextInputType? keyboardType;
  final Widget? suffix;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return TextField(
      controller: controller,
      obscureText: obscure,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, size: 20),
        suffixIcon: suffix,
        filled: true,
        fillColor: theme.colorScheme.surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(15),
          borderSide: BorderSide(
              color:
                  theme.colorScheme.outlineVariant.withValues(alpha: 0.6)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(15),
          borderSide: BorderSide(
              color:
                  theme.colorScheme.outlineVariant.withValues(alpha: 0.6)),
        ),
      ),
    );
  }
}