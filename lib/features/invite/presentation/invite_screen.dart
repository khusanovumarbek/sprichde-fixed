import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Do'stlarni taklif qilish sahifasi.
/// Minimalistik dizayn: taklif havolasi, nusxalash va ulashish tugmalari.
class InviteScreen extends StatelessWidget {
  const InviteScreen({super.key});

  // Demo taklif havolasi (keyinchalik foydalanuvchi ID si bilan dinamik qilinadi)
  static const String inviteLink = 'https://sprichde.app/invite/KARIMOV42';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Do‘stni taklif qilish'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
          children: [
            // ---------- Sarlavha qismi ----------
            Center(
              child: Container(
                width: 76,
                height: 76,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary.withValues(alpha: 0.10),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Icon(Icons.card_giftcard_rounded,
                    size: 38, color: theme.colorScheme.primary),
              ),
            ),
            const SizedBox(height: 18),
            Text(
              'Do‘stingizni taklif qiling',
              textAlign: TextAlign.center,
              style: theme.textTheme.headlineSmall
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 8),
            Text(
              'Havolani ulashing — do‘stingiz ro‘yxatdan o‘tsa, ikkalangiz ham bonus darslarga ega bo‘lasiz.',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                height: 1.5,
              ),
            ),
            const SizedBox(height: 26),

            // ---------- Havola maydoni ----------
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                    color: theme.colorScheme.outlineVariant.withValues(alpha: 0.6)),
              ),
              child: Row(
                children: [
                  Icon(Icons.link_rounded,
                      size: 20,
                      color: theme.colorScheme.primary.withValues(alpha: 0.8)),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      inviteLink,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () => _copy(context),
                    style: TextButton.styleFrom(
                      minimumSize: const Size(0, 36),
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                    ),
                    child: const Text('Nusxalash',
                        style: TextStyle(fontWeight: FontWeight.w700)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 22),

            // ---------- Asosiy ulashish tugmasi ----------
            SizedBox(
              height: 54,
              child: FilledButton.icon(
                onPressed: () => _share(context),
                style: FilledButton.styleFrom(
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                ),
                icon: const Icon(Icons.ios_share_rounded),
                label: const Text('Ulashish',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
              ),
            ),
            const SizedBox(height: 22),

            // ---------- Ijtimoiy tarmoqlar ----------
            Text(
              'Tez ulashish',
              style: theme.textTheme.titleSmall
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _SocialButton(
                    icon: Icons.send_rounded,
                    label: 'Telegram',
                    onTap: () => _share(context)),
                const SizedBox(width: 12),
                _SocialButton(
                    icon: Icons.chat_bubble_rounded,
                    label: 'WhatsApp',
                    onTap: () => _share(context)),
                const SizedBox(width: 12),
                _SocialButton(
                    icon: Icons.sms_rounded,
                    label: 'SMS',
                    onTap: () => _share(context)),
              ],
            ),
            const SizedBox(height: 28),

            // ---------- Statistika ----------
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.06),
                borderRadius: BorderRadius.circular(18),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: _StatItem(value: '0', label: 'Taklif qilingan'),
                  ),
                  Container(
                    width: 1,
                    height: 36,
                    color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
                  ),
                  Expanded(
                    child: _StatItem(value: '0', label: 'Qo‘shilgan'),
                  ),
                  Container(
                    width: 1,
                    height: 36,
                    color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
                  ),
                  Expanded(
                    child: _StatItem(value: '0', label: 'Bonus (kun)'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _copy(BuildContext context) {
    Clipboard.setData(const ClipboardData(text: inviteLink));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Havola nusxalandi'),
        behavior: SnackBarBehavior.floating,
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _share(BuildContext context) {
    // Hozircha umumiy ulashish oynasi (keyinchalik share_plus paketi bilan
    // Telegram/WhatsApp to'g'ridan-to'g'ri tanlanadi).
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(20, 4, 20, 12),
              child: Text('Ulashish',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
            ),
            _ShareTile(
              icon: Icons.send_rounded,
              label: 'Telegram',
              onTap: () {
                Navigator.pop(context);
                _toast(context, 'Telegram ochilmoqda…');
              },
            ),
            _ShareTile(
              icon: Icons.chat_bubble_rounded,
              label: 'WhatsApp',
              onTap: () {
                Navigator.pop(context);
                _toast(context, 'WhatsApp ochilmoqda…');
              },
            ),
            _ShareTile(
              icon: Icons.sms_rounded,
              label: 'SMS orqali',
              onTap: () {
                Navigator.pop(context);
                _toast(context, 'Xabarlar ochilmoqda…');
              },
            ),
            _ShareTile(
              icon: Icons.link_rounded,
              label: 'Havolani nusxalash',
              onTap: () {
                Navigator.pop(context);
                _copy(context);
              },
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  void _toast(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }
}

// --------------------------------------------------------------------------- //
// Yordamchi widgetlar
// --------------------------------------------------------------------------- //

class _SocialButton extends StatelessWidget {
  const _SocialButton(
      {required this.icon, required this.label, required this.onTap});

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
                color: theme.colorScheme.outlineVariant.withValues(alpha: 0.6)),
          ),
          child: Column(
            children: [
              Icon(icon, color: theme.colorScheme.primary, size: 24),
              const SizedBox(height: 8),
              Text(label,
                  style: const TextStyle(
                      fontSize: 11.5, fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  const _StatItem({required this.value, required this.label});

  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      children: [
        Text(value,
            style: theme.textTheme.titleLarge
                ?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 2),
        Text(label,
            style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.55))),
      ],
    );
  }
}

class _ShareTile extends StatelessWidget {
  const _ShareTile(
      {required this.icon, required this.label, required this.onTap});

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return ListTile(
      onTap: onTap,
      leading: Container(
        width: 42,
        height: 42,
        decoration: BoxDecoration(
          color: theme.colorScheme.primary.withValues(alpha: 0.10),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(icon, color: theme.colorScheme.primary, size: 21),
      ),
      title: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
      trailing: const Icon(Icons.chevron_right, size: 20),
    );
  }
}