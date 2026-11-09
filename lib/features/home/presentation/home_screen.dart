import 'package:flutter/material.dart';

import '../../invite/presentation/invite_screen.dart';
import '../../journey/presentation/journey_screen.dart';
import '../../lessons/data/lesson_repository.dart';

/// Bosh sahifa — minimalistik dizayn.
/// Do'stni taklif qilish va 182 kunlik sayohat bo'limlari bilan.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final lessons = const LessonRepository().lessons;

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
      children: [
        // ---------------- Salomlashish ----------------
        Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Guten Tag! 👋',
                      style: theme.textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w800)),
                  const SizedBox(height: 4),
                  Text('Bugun nemis tilida yana bir qadam.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface
                              .withValues(alpha: 0.6))),
                ],
              ),
            ),
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.10),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(Icons.person_outline_rounded,
                  color: theme.colorScheme.primary),
            ),
          ],
        ),
        const SizedBox(height: 22),

        // ---------------- Bugungi maqsad ----------------
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: theme.colorScheme.primary,
            borderRadius: BorderRadius.circular(22),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Bugungi maqsad',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.85),
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.4)),
              const SizedBox(height: 6),
              const Text('15 daqiqalik mashg‘ulot',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 19,
                      fontWeight: FontWeight.w800)),
              const SizedBox(height: 18),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: 0.35,
                  minHeight: 8,
                  backgroundColor: Colors.white.withValues(alpha: 0.22),
                  valueColor:
                      const AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
              const SizedBox(height: 10),
              Text('5 / 15 daqiqa',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.85),
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600)),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // ---------------- 182 kunlik sayohat ----------------
        _FeatureCard(
          icon: Icons.route_rounded,
          title: '182 kunlik sayohat',
          subtitle: 'Har kuni bir qadam — katta natija sari',
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute<void>(
                builder: (_) => const JourneyScreen()),
          ),
        ),
        const SizedBox(height: 12),

        // ---------------- Do‘stni taklif qilish ----------------
        _FeatureCard(
          icon: Icons.card_giftcard_rounded,
          title: 'Do‘stni taklif qilish',
          subtitle: 'Havolani ulashing va bonus oling',
          accent: true,
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute<void>(
                builder: (_) => const InviteScreen()),
          ),
        ),
        const SizedBox(height: 26),

        // ---------------- Davom eting ----------------
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Davom eting',
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w800)),
            Text('Barchasi',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: theme.colorScheme.primary)),
          ],
        ),
        const SizedBox(height: 12),
        for (final lesson in lessons.take(2))
          Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                  color: theme.colorScheme.outlineVariant
                      .withValues(alpha: 0.6)),
            ),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withValues(alpha: 0.10),
                    borderRadius: BorderRadius.circular(13),
                  ),
                  child: Icon(Icons.play_arrow_rounded,
                      color: theme.colorScheme.primary),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(lesson.title,
                          style: const TextStyle(
                              fontWeight: FontWeight.w700, fontSize: 14.5)),
                      const SizedBox(height: 3),
                      Text(lesson.level,
                          style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurface
                                  .withValues(alpha: 0.55))),
                    ],
                  ),
                ),
                Icon(Icons.chevron_right_rounded,
                    color:
                        theme.colorScheme.onSurface.withValues(alpha: 0.35)),
              ],
            ),
          ),
      ],
    );
  }
}

/// Minimalistik xususiyat kartasi.
class _FeatureCard extends StatelessWidget {
  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.accent = false,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool accent;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bg = accent
        ? theme.colorScheme.primary.withValues(alpha: 0.08)
        : theme.colorScheme.surface;
    final border = accent
        ? theme.colorScheme.primary.withValues(alpha: 0.20)
        : theme.colorScheme.outlineVariant.withValues(alpha: 0.6);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: border),
        ),
        child: Row(
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: theme.colorScheme.primary, size: 24),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: const TextStyle(
                          fontWeight: FontWeight.w700, fontSize: 15)),
                  const SizedBox(height: 3),
                  Text(subtitle,
                      style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurface
                              .withValues(alpha: 0.55))),
                ],
              ),
            ),
            Icon(Icons.chevron_right_rounded,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.35)),
          ],
        ),
      ),
    );
  }
}